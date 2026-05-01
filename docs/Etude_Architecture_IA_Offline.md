# Étude d'Architecture — Assistant IA 100% Offline pour Dolibarr Immobilier

> Date : Mai 2026 | Version 1.0 | Contrainte matérielle : CPU 4 cœurs / 8 Go RAM / Pas de GPU

---

## 1. Principe fondamental : Confidentialité absolue

L'assistant IA **ne transmet jamais de données sensibles** (noms de clients, adresses de biens, montants de loyers, historiques de paiement) vers un service externe. Tout le traitement s'effectue en réseau local, dans le conteneur Docker `ollama`.

**Données qui ne sortent jamais :**
- Noms, téléphones, emails des clients (`llx_societe`)
- Adresses exactes des biens (`llx_immo_bien`)
- Montants des loyers, cautions, commissions (`llx_immo_bail`, `llx_immo_quittance`)
- Historique des paiements (`llx_immo_quittance`, `llx_immo_paiement_mobile`)
- Contrats et documents (`llx_document`)

**Données pouvant être utilisées localement par le modèle :**
- Statistiques agrégées (prix moyen au m² par quartier)
- Catalogues de référence (types de bien, états)
- Descriptions textuelles des biens (générées ou saisies)

---

## 2. Stack technique

| Couche | Technologie | Rôle |
|--------|-------------|------|
| **Modèle LLM** | Llama 3.1 8B (Q4_0 quantifié) | Raisonnement en langage naturel, génération de texte |
| **Serveur LLM** | Ollama 0.1.x | API REST locale exposée sur `http://ollama:11434` |
| **Conteneur** | Docker image `ollama/ollama` | Exécution isolée dans le même docker-compose |
| **Client API** | PHP cURL + JSON | Communication Dolibarr ↔ Ollama |
| **Base RAG** | PostgreSQL (`llx_immo_ai_context`) | Contexte dynamique injecté dans les prompts |
| **Cache** | Fichiers PHP (`temp/ai_cache/`) | Réponses fréquentes mémorisées pour réduire les appels |

---

## 3. Choix du modèle : Pourquoi Llama 3.1 8B Q4_0 ?

| Critère | Llama 3.1 8B Q4_0 | Alternatives rejetées |
|---------|-------------------|----------------------|
| **Taille mémoire** | ~4.3 Go RAM (quantifié 4-bit) | Mixtral 8x7B → ~24 Go (trop gros) |
| **CPU 4 cœurs** | Latence 2-5 secondes acceptable | LLaMA-2 70B → impossible sans GPU |
| **Français** | Bon support du français | Gemma 7B → français moins fluide |
| **RAG** | Contexte 128K tokens (suffisant) | Mistral 7B v0.3 → comparable, moins testé en RAG |
| **Licence** | Open source (Meta Llama 3.1) | GPT-4/Claude → payant + cloud uniquement |
| **Raisonnement** | Correct pour du code SQL simple | Code LLaMA → moins bon en suivis d'instructions |

**Commande de pull :**
```bash
docker exec -it ollama ollama pull llama3.1:8b
# Alternative plus légère pour tests rapides :
# docker exec -it ollama ollama pull llama3.2:3b  (moins précis mais ~1.8 Go)
```

---

## 4. Architecture RAG (Retrieval Augmented Generation)

Le principe du RAG est simple : au lieu de laisser le modèle deviner ou halluciner, on **injecte les données réelles** de l'agence dans le prompt avant chaque requête.

### 4.1 Pipeline RAG

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  1. Question     │────▶│  2. Retrieval    │────▶│  3. Génération   │
│     Agent        │     │   (PostgreSQL)   │     │   (Ollama LLM)   │
│   « Je cherche   │     │ Requête SQL      │     │ Prompt enrichi   │
│ un 3 pièces à    │     │ qui récupère     │     │ avec contexte    │
│  Cocody »        │     │ biens + contexte │     │ + question       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  llx_immo_bien   │
                    │  llx_immo_bail   │
                    │  llx_immo_quittance│
                    └──────────────────┘
```

### 4.2 Table de contexte RAG

```sql
-- Table pivot pour le RAG (alimentée automatiquement par triggers)
CREATE TABLE llx_immo_ai_context (
    rowid serial PRIMARY KEY,
    context_type varchar(32) NOT NULL,  -- 'bien', 'client', 'bail', 'quittance'
    fk_element integer NOT NULL,         -- ID de l'élément concerné
    context_text text NOT NULL,          -- Texte formaté pour le LLM
    embedding vector(384),               -- Embedding sémantique (optionnel, extension pgvector)
    date_index timestamp DEFAULT CURRENT_TIMESTAMP,
    tms timestamp DEFAULT CURRENT_TIMESTAMP
);

-- Index pour recherche rapide
CREATE INDEX idx_ai_context_type ON llx_immo_ai_context(context_type);
CREATE INDEX idx_ai_context_fk ON llx_immo_ai_context(fk_element);
```

**Exemple de context_text pour un bien :**
```
Bien: B2026-0042
Type: Appartement
Surface: 85 m²
Ville: Cocody, Angré
Prix location: 180 000 FCFA/mois
Prix vente: 35 000 000 FCFA
État: Disponible à louer
Caractéristiques: 3 chambres, 2 salles de bain, balcon, parking
Description: Bel appartement rénové, proche du supermarché.
```

> **Note** : Les données personnelles (nom propriétaire, téléphone locataire) sont **anonymisées** dans ce contexte. Seules les caractéristiques métier du bien sont incluses.

### 4.3 Alimentation automatique du RAG

**Triggers PostgreSQL** (sur `llx_immo_bien`, `llx_immo_bail`) qui mettent à jour `llx_immo_ai_context` à chaque INSERT/UPDATE :

```sql
-- Trigger sur llx_immo_bien
CREATE OR REPLACE FUNCTION update_ai_context_bien()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO llx_immo_ai_context (context_type, fk_element, context_text)
    VALUES (
        'bien',
        NEW.rowid,
        format(
            'Bien: %s\nType: %s\nSurface: %s m²\nVille: %s\nPrix location: %s FCFA\nPrix vente: %s FCFA\nÉtat: %s\nDescription: %s',
            NEW.ref, NEW.type_bien, NEW.superficie_habitable,
            NEW.ville, NEW.prix_location, NEW.prix_vente,
            NEW.etat, NEW.description
        )
    )
    ON CONFLICT (context_type, fk_element) DO UPDATE
    SET context_text = EXCLUDED.context_text, tms = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_ai_context_bien
AFTER INSERT OR UPDATE ON llx_immo_bien
FOR EACH ROW EXECUTE FUNCTION update_ai_context_bien();
```

---

## 5. Prompts templates par cas d'usage

### 5.1 Recommandation de biens (Chatbot)

```
Tu es un assistant immobilier expert en Côte d'Ivoire.
Voici les biens actuellement disponibles dans l'agence :
{contexte_rag}

Requête du client : "{question_utilisateur}"

Instructions :
1. Analyse la requête du client (type de bien, budget, quartier)
2. Sélectionne les 3 biens les plus pertinents parmi ceux disponibles
3. Pour chaque bien, donne : référence, type, surface, prix, et un argument de vente
4. Si aucun bien ne correspond, propose des alternatives (même quartier, budget proche)
5. Réponds UNIQUEMENT en français, de manière concise et professionnelle

Format de réponse :
**Bien 1** : [Référence] — [Type], [Surface] m², [Prix] FCFA
[Argument de vente personnalisé]
```

### 5.2 Génération de description d'annonce

```
Tu es un rédacteur d'annonces immobilières pour le marché ivoirien.
Caractéristiques du bien :
{contexte_bien}

Instructions :
1. Rédige une annonce attractive de 80-120 mots
2. Commence par un titre accrocheur
3. Mentionne les atouts clés (localisation, proximité commodités)
4. Utilise un ton chaleureux mais professionnel
5. Termine par un appel à l'action (visite, contact)
6. N'invente JAMAIS de caractéristiques non listées ci-dessus

Format :
**Titre** : [Titre accrocheur]
[Corps de l'annonce]
[Appel à l'action]
```

### 5.3 Estimation de prix (avec comparables)

```
Tu es un expert en estimation immobilière à Abidjan et en Côte d'Ivoire.
Bien à estimer :
{caractéristiques_bien}

Comparables récents (ventes similaires) :
{contexte_comparables}

Instructions :
1. Analyse les comparables fournis
2. Calcule une fourchette de prix au m² (min, moyen, max)
3. Applique cette fourchette à la surface du bien à estimer
4. Mentionne les facteurs d'ajustement (état, étage, vue, etc.)
5. Réponds avec précaution — mentionne que c'est une ESTIMATION indicative

Format :
**Fourchette estimée** : [min] - [max] FCFA
**Prix au m²** : [min] - [max] FCFA/m²
**Facteurs pris en compte** : [liste]
**Note** : Estimation indicative basée sur {N} comparables récents.
```

---

## 6. Client PHP vers Ollama

### 6.1 Classe `ImmoAiClient`

```php
<?php
declare(strict_types=1);

/**
 * Client API pour Ollama (100% offline)
 * Module mod_immo_ai — modImmocoreAI
 */
class ImmoAiClient
{
    private const OLLAMA_URL = 'http://ollama:11434/api/generate';
    private const MODEL = 'llama3.1:8b';
    private const TIMEOUT = 30;  // secondes
    private const MAX_TOKENS = 1024;

    /**
     * Envoie un prompt à Ollama et retourne la réponse texte
     */
    public function generate(string $prompt, string $system = ''): string
    {
        $payload = [
            'model' => self::MODEL,
            'prompt' => $prompt,
            'system' => $system,
            'stream' => false,
            'options' => [
                'num_predict' => self::MAX_TOKENS,
                'temperature' => 0.7,
            ],
        ];

        $ch = curl_init(self::OLLAMA_URL);
        curl_setopt_array($ch, [
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => json_encode($payload),
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
            CURLOPT_TIMEOUT => self::TIMEOUT,
        ]);

        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);

        if ($httpCode !== 200 || $response === false) {
            return '[Erreur: l\'assistant IA n\'est pas disponible]';
        }

        $data = json_decode($response, true);
        return $data['response'] ?? '[Réponse vide]';
    }

    /**
     * Vérifie que le service Ollama est actif
     */
    public function isAvailable(): bool
    {
        $ch = curl_init('http://ollama:11434');
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
        curl_setopt($ch, CURLOPT_TIMEOUT, 5);
        $response = curl_exec($ch);
        curl_close($ch);
        return $response !== false;
    }
}
```

### 6.2 Exemple d'utilisation (Recommandation biens)

```php
// Dans le module immobien, page de recherche
$aiClient = new ImmoAiClient();

// 1. Récupérer le contexte RAG (biens disponibles)
$context = getAiContextForBienSearch($ville, $typeBien, $budgetMax);

// 2. Construire le prompt
$prompt = buildRecommandationPrompt($context, $questionClient);

// 3. Appeler Ollama
$response = $aiClient->generate($prompt, SYSTEM_PROMPT_RECOMMANDATION);

// 4. Afficher la réponse (HTML sécurisé)
print '<div class="ai-response">' . dol_escape_htmltag($response) . '</div>';
```

---

## 7. Docker Compose (service Ollama)

Ajout dans `docker-compose.yml` :

```yaml
services:
  # ... (db, dolibarr, pgadmin inchangés)

  ollama:
    image: ollama/ollama:latest
    container_name: immo-ollama
    volumes:
      - ollama_models:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - immo-network
    environment:
      - OLLAMA_NUM_PARALLEL=1
      - OLLAMA_MAX_LOADED_MODELS=1
    deploy:
      resources:
        limits:
          memory: 6G  # Limite pour laisser de la RAM à Dolibarr + PostgreSQL
        reservations:
          memory: 4G  # Minimum pour charger Llama 3.1 8B Q4_0
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434"]
      interval: 30s
      timeout: 10s
      retries: 3
    # note: pas de GPU, le modèle tourne sur CPU 4 cœurs

volumes:
  ollama_models:
    driver: local
```

---

## 8. Performance et contraintes CPU 4 cœurs / 8 Go RAM

### 8.1 Consommation ressources estimée

| Service | RAM | CPU | Commentaire |
|---------|-----|-----|-------------|
| PostgreSQL | 1 Go | 1 cœur | Configuration standard |
| Dolibarr (Apache + PHP) | 1 Go | 1 cœur | 2 workers FPM |
| Ollama (Llama 3.1 8B) | 4.5 Go | 2 cœurs | Modèle chargé en mémoire |
| Système + marge | 1.5 Go | — | Cache OS, buffers |
| **Total** | **~8 Go** | **4 cœurs** | Limite du serveur |

### 8.2 Optimisations pour CPU limité

| Optimisation | Gain | Implémentation |
|--------------|------|----------------|
| **Quantification 4-bit** | RAM divisée par 2 | Modèle `llama3.1:8b` (déjà Q4_0 par défaut) |
| **Cache des réponses** | Évite 80% des appels LLM | Fichiers PHP dans `temp/ai_cache/` avec TTL 1h |
| **Batch RAG** | Réduit les requêtes SQL | Précharger 10 biens en 1 requête SQL |
| **Contexte réduit** | Moins de tokens = génération plus rapide | Limiter à 3 biens dans le contexte |
| **Modèle 3B pour tests** | Alternative très légère | `llama3.2:3b` (~1.8 Go) pour les agences avec < 8 Go RAM |

### 8.3 Temps de réponse cibles

| Cas d'usage | Requête SQL | Génération LLM | Total estimé |
|-------------|-------------|----------------|--------------|
| Recommandation 3 biens | < 100 ms | 2-4 s | **2-4 s** |
| Génération description | < 50 ms | 3-5 s | **3-5 s** |
| Estimation prix (RAG) | < 200 ms | 4-6 s | **4-6 s** |
| Réponse cache | < 10 ms | 0 ms | **< 10 ms** |

> **Experience utilisateur** : Un temps < 5 secondes est acceptable pour un assistant IA. Au-delà, il faut afficher un indicateur de chargement (spinner) et utiliser le cache agressivement.

---

## 9. Sécurité et validation

### 9.1 Protection contre l'injection SQL via LLM

**Jamais de SQL généré par le LLM exécuté directement.** Le RAG fonctionne en 2 étapes :

1. **PHP extrait les données** : requêtes SQL pré-validées, paramètres bindés
2. **Le LLM ne reçoit que du texte** : il formate la réponse, mais ne génère jamais de code exécutable

```php
// ✅ BON : PHP fait le SQL, Ollama fait le texte
$biens = $db->query("SELECT * FROM llx_immo_bien WHERE etat = 'A_LOUER' AND ville = ?", [$ville]);
$context = formatBiensForRag($biens);
$response = $aiClient->generate($prompt . $context);

// ❌ INTERDIT : jamais exécuter du SQL généré par le LLM
// $sql = $aiClient->generate("Génère une requête SQL pour...");
// $db->query($sql); ← DANGER ABSOLU
```

### 9.2 Validation des réponses

```php
/**
 * Vérifie que la réponse Ollama ne contient pas de données hallucinées
 */
function validateAiResponse(string $response, array $allowedRefs): bool
{
    // Extrait les références de biens mentionnées
    preg_match_all('/B\d{4}-\d{4}/', $response, $matches);
    $mentionedRefs = $matches[0] ?? [];

    // Vérifie que toutes les références existent dans la base
    foreach ($mentionedRefs as $ref) {
        if (!in_array($ref, $allowedRefs, true)) {
            return false; // Hallucination détectée
        }
    }
    return true;
}
```

### 9.3 Journal d'audit (transparence)

```sql
-- Table de logs des interactions IA
CREATE TABLE llx_immo_ai_logs (
    rowid serial PRIMARY KEY,
    fk_user integer,
    question text,
    context_hash varchar(64),  -- Hash du contexte RAG utilisé
    model_version varchar(32), -- ex: "llama3.1:8b"
    response_preview text,     -- 200 premiers caractères
    response_time_ms integer,  -- Temps de réponse
    was_cached boolean,
    datec timestamp DEFAULT CURRENT_TIMESTAMP
);
```

> **Objectif** : Permettre à l'agent de revenir sur une recommandation et comprendre ce que l'IA a utilisé comme contexte.

---

## 10. Fallback et dégradation gracieuse

### 10.1 Si Ollama n'est pas disponible

```php
if (!$aiClient->isAvailable()) {
    // Fallback : recherche SQL classique + texte fixe
    $biens = searchBiensSQL($ville, $type, $budget);
    print '<div class="ai-offline">';
    print '<p><strong>Assistant IA indisponible</strong> (mode hors-ligne)</p>';
    print '<p>Biens correspondants trouvés : ' . count($biens) . '</p>';
    // Affichage classique des biens
    print '</div>';
}
```

### 10.2 Si le modèle est trop lent (> 10 secondes)

- Timeout cURL à 30 secondes
- Si timeout atteint : réponse "L'assistant réfléchit... Veuillez patienter."
- Proposition de recharger la page ou de contacter l'administrateur

---

## 11. Résumé et recommandation

| Aspect | Décision |
|--------|----------|
| **Modèle** | Llama 3.1 8B Q4_0 via Ollama |
| **Architecture** | RAG (contexte dynamique depuis PostgreSQL) |
| **Confidentialité** | 100% offline, données jamais sortantes |
| **Matériel min.** | CPU 4 cœurs / 8 Go RAM (compatible) |
| **Latence cible** | < 5 secondes par requête |
| **Optimisation** | Cache PHP, batch SQL, contexte limité |
| **Fallback** | Recherche SQL classique si IA indisponible |
| **Sécurité** | Pas de SQL généré par LLM, validation des références |

**Recommandation** : L'architecture est **techniquement réalisable** sur du matériel modeste (4 cœurs / 8 Go). Le compromis performance/confidentialité est acceptable pour l'usage immobilier. La clé du succès réside dans :
1. Un **RAG bien conçu** (contexte pertinent, pas trop verbeux)
2. Un **cache efficace** (éviter les appels inutiles au LLM)
3. Un **fallback robuste** (l'agent peut toujours travailler sans l'IA)

---

*Étude d'Architecture — Assistant IA Offline | v1.0 | Mai 2026*
