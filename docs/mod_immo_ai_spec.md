# Module `mod_immo_ai` — Assistant Intelligent (700010)

> Version 1.0 | Dépendant de `immocore`, `immobien`, `immoclient`, `immolocatif` | 100% Offline via Ollama

---

## 1. Objectif

Fournir un **assistant intelligent intégré à Dolibarr** qui aide les agents immobiliers dans leurs tâches quotidiennes (recommandation de biens, génération d'annonces, estimation de prix) **sans jamais transmettre de données sensibles à l'extérieur** du serveur de l'agence.

L'assistant fonctionne dans un conteneur Docker **Ollama** exécutant un modèle de langage open source (Llama 3.1 8B) en réseau local, avec un mécanisme RAG (Retrieval Augmented Generation) injectant le contexte des biens, clients et transactions depuis PostgreSQL.

---

## 2. Dépendances

| Module | Numéro | Utilisation |
|--------|--------|-------------|
| `immocore` | 700000 | Configuration, droits, menu, hooks |
| `immobien` | 700001 | Données des biens (contexte RAG) |
| `immoclient` | 700002 | Données des tiers (contexte RAG anonymisé) |
| `immolocatif` | 700003 | Données des baux et quittances (estimation prix) |

**Services externes (déployés en local)** :
- `ollama:11434` — Serveur LLM local (Docker)

---

## 3. Fonctionnalités

### 3.1 Chatbot intelligent (widget flottant)

Widget en bas à droite de l'écran Dolibarr accessible depuis toutes les pages du module Immobilier.

**Exemples de requêtes supportées** :
- « Quels appartements de 2-3 pièces sont disponibles à Cocody ? »
- « Quel est le prix moyen au m² à Angré pour un appartement ? »
- « Résume-moi les impayés du mois »
- « Comment estimer le loyer d'un 80 m² à Marcory ? »

**Mécanisme** :
1. L'agent tape sa question
2. PHP analyse la question et détermine le type (recherche bien, estimation, statistique)
3. Requête SQL pré-validée extrait le contexte pertinent depuis PostgreSQL
4. Le contexte + la question sont envoyés à Ollama via API REST locale
5. La réponse est affichée en temps réel (streaming optionnel)

### 3.2 Génération automatique de descriptions

Bouton **« Générer description avec IA »** sur la fiche bien (`card.php`).

**Flux** :
1. PHP extrait les caractéristiques du bien (type, surface, ville, état, prix)
2. Construit un prompt avec template
3. Appelle Ollama en local
4. Retourne un texte marketing de 80-120 mots
5. L'agent peut modifier le texte avant de l'enregistrer

### 3.3 Recommandation de biens (matching client)

Sur la fiche client, onglet **« Recommandations IA »**.

**Mécanisme RAG + scoring PHP** :
1. PHP récupère le profil du client (budget, type recherché, quartiers préférés depuis les visites)
2. Requête SQL sélectionne les biens disponibles correspondants
3. Scoring PHP pondère chaque bien (surface proche, prix dans la fourchette, quartier match)
4. Le top 3 biens est envoyé à Ollama pour formulation de la réponse
5. L'agent reçoit : « Basé sur le profil de [Client], je recommande : [Bien 1]... »

---

## 4. Architecture technique

```
┌──────────────────────────────────────────────────────────┐
│                   Dolibarr 23.x (Docker)                 │
│                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐ │
│  │ ImmoBien    │    │ ImmoClient  │    │ ImmoBail    │ │
│  │ (700001)    │    │ (700002)    │    │ (700003)    │ │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘ │
│         │                  │                  │        │
│         └──────────────────┼──────────────────┘        │
│                            │                          │
│                     ┌──────┴──────┐                   │
│                     │ mod_immo_ai │                   │
│                     │  (700010)   │                   │
│                     │             │                   │
│                     │ ┌─────────┐ │                   │
│                     │ │Chatbot  │ │                   │
│                     │ │Widget   │ │                   │
│                     │ └─────────┘ │                   │
│                     │ ┌─────────┐ │                   │
│                     │ │Prompt   │ │                   │
│                     │ │Builder  │ │                   │
│                     │ └─────────┘ │                   │
│                     │ ┌─────────┐ │                   │
│                     │ │Recommand│ │                   │
│                     │ │Engine   │ │                   │
│                     │ └─────────┘ │                   │
│                     └──────┬──────┘                   │
│                            │ cURL (réseau local)     │
│                     ┌──────┴──────┐                   │
│                     │   Ollama    │                   │
│                     │  :11434     │                   │
│                     │ Llama3.1 8B │                   │
│                     └─────────────┘                   │
│                            │                          │
│                     ┌──────┴──────┐                   │
│                     │  PostgreSQL │                   │
│                     │ llx_immo_*  │                   │
│                     └─────────────┘                   │
└──────────────────────────────────────────────────────────┘
```

---

## 5. Schéma de données

### 5.1 Table de contexte RAG

```sql
CREATE TABLE IF NOT EXISTS llx_immo_ai_context (
    rowid serial PRIMARY KEY,
    context_type varchar(32) NOT NULL CHECK (context_type IN ('bien','client','bail','quittance','estimation')),
    fk_element integer NOT NULL,
    context_text text NOT NULL,
    date_index timestamp DEFAULT CURRENT_TIMESTAMP,
    tms timestamp DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(context_type, fk_element)
);

CREATE INDEX idx_ai_context_type ON llx_immo_ai_context(context_type);
CREATE INDEX idx_ai_context_fk ON llx_immo_ai_context(fk_element);
CREATE INDEX idx_ai_context_date ON llx_immo_ai_context(date_index);
```

### 5.2 Table de logs d'audit

```sql
CREATE TABLE IF NOT EXISTS llx_immo_ai_logs (
    rowid serial PRIMARY KEY,
    fk_user integer,
    interaction_type varchar(32) NOT NULL CHECK (interaction_type IN ('chat','description','recommandation','estimation')),
    question text,
    context_hash varchar(64),
    model_version varchar(32) DEFAULT 'llama3.1:8b',
    response_preview varchar(500),
    response_time_ms integer,
    was_cached smallint DEFAULT 0,
    datec timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_logs_user ON llx_immo_ai_logs(fk_user);
CREATE INDEX idx_ai_logs_type ON llx_immo_ai_logs(interaction_type);
CREATE INDEX idx_ai_logs_date ON llx_immo_ai_logs(datec);
```

### 5.3 Table de cache IA

```sql
CREATE TABLE IF NOT EXISTS llx_immo_ai_cache (
    rowid serial PRIMARY KEY,
    cache_key varchar(64) NOT NULL UNIQUE,  -- MD5 du prompt
    response text NOT NULL,
    hit_count integer DEFAULT 1,
    datec timestamp DEFAULT CURRENT_TIMESTAMP,
    tms timestamp DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_cache_key ON llx_immo_ai_cache(cache_key);
CREATE INDEX idx_ai_cache_date ON llx_immo_ai_cache(datec);
```

---

## 6. Classes PHP

### 6.1 `ImmoAiClient` — Client API Ollama

```php
<?php
declare(strict_types=1);

require_once DOL_DOCUMENT_ROOT . '/core/class/commonobject.class.php';

class ImmoAiClient
{
    public const OLLAMA_URL = 'http://ollama:11434/api/generate';
    public const MODEL = 'llama3.1:8b';
    public const TIMEOUT = 30;
    public const MAX_TOKENS = 1024;
    public const TEMPERATURE = 0.7;

    /**
     * Envoie un prompt à Ollama et retourne la réponse texte
     */
    public function generate(string $prompt, string $system = '', int $maxTokens = self::MAX_TOKENS): string
    {
        $payload = [
            'model' => self::MODEL,
            'prompt' => $prompt,
            'system' => $system,
            'stream' => false,
            'options' => [
                'num_predict' => $maxTokens,
                'temperature' => self::TEMPERATURE,
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
            return '[Erreur: l\'assistant IA est temporairement indisponible]';
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

### 6.2 `ImmoAiContext` — Gestion du contexte RAG

```php
<?php
declare(strict_types=1);

class ImmoAiContext
{
    private DoliDB $db;

    public function __construct(DoliDB $db)
    {
        $this->db = $db;
    }

    /**
     * Construit le contexte texte pour les biens disponibles
     */
    public function buildContextForBienSearch(string $ville = '', string $typeBien = '', float $budgetMax = 0): string
    {
        $sql = "SELECT ref, type_bien, superficie_habitable, ville, prix_location, prix_vente, etat, description ";
        $sql .= "FROM " . $this->db->prefix() . "immo_bien WHERE etat IN ('A_LOUER', 'A_VENDRE', 'DISPONIBLE')";
        $params = [];

        if ($ville !== '') {
            $sql .= " AND ville LIKE ?";
            $params[] = '%' . $ville . '%';
        }
        if ($typeBien !== '') {
            $sql .= " AND type_bien = ?";
            $params[] = $typeBien;
        }
        if ($budgetMax > 0) {
            $sql .= " AND (prix_location <= ? OR prix_vente <= ?)";
            $params[] = $budgetMax;
            $params[] = $budgetMax;
        }
        $sql .= " ORDER BY datec DESC LIMIT 10";

        $resql = $this->db->query($sql);
        $context = "Biens disponibles :\n";

        if ($resql) {
            while ($obj = $this->db->fetch_object($resql)) {
                $context .= sprintf(
                    "- %s | %s | %s m² | %s | Loc: %s FCFA | Vente: %s FCFA | %s\n",
                    $obj->ref, $obj->type_bien, $obj->superficie_habitable,
                    $obj->ville, $obj->prix_location, $obj->prix_vente,
                    substr($obj->description ?? '', 0, 100)
                );
            }
        }
        return $context;
    }

    /**
     * Construit le contexte pour les comparables de prix
     */
    public function buildContextForEstimation(string $typeBien, string $ville, float $surface): string
    {
        // Comparables : baux récents + ventes comparables
        $sql = "SELECT 'location' as source, loyer_nu as prix, surface, quartier FROM llx_immo_bail b ";
        $sql .= "JOIN llx_immo_bien bi ON b.fk_bien = bi.rowid WHERE bi.type_bien = ? AND bi.ville LIKE ? ";
        $sql .= "UNION ALL SELECT 'vente' as source, prix_vente as prix, surface, quartier FROM llx_immo_vente_comp WHERE type_bien = ? AND ville LIKE ? ";
        $sql .= "ORDER BY prix LIMIT 20";

        $resql = $this->db->query($sql);
        $context = "Comparables récents :\n";

        if ($resql) {
            while ($obj = $this->db->fetch_object($resql)) {
                $context .= sprintf("- %s | %s m² | %s | %s FCFA\n", $obj->source, $obj->surface, $obj->quartier, $obj->prix);
            }
        }
        return $context;
    }
}
```

### 6.3 `ImmoAiEngine` — Moteur de recommandation (scoring PHP)

```php
<?php
declare(strict_types=1);

class ImmoAiEngine
{
    private DoliDB $db;

    public function __construct(DoliDB $db)
    {
        $this->db = $db;
    }

    /**
     * Calcule un score de matching entre un client et un bien
     * Score de 0 à 100
     */
    public function calculerScoreMatching(int $clientId, int $bienId): float
    {
        $score = 0.0;

        // Récupérer profil client (budget, type préféré, quartiers visités)
        $client = $this->getClientProfile($clientId);
        $bien = $this->getBienDetails($bienId);

        if (!$client || !$bien) return 0.0;

        // Budget (40% du score)
        if ($client['budget_max'] > 0 && $bien['prix_location'] > 0) {
            $ratio = min($bien['prix_location'] / $client['budget_max'], 1.0);
            $score += $ratio * 40;
        }

        // Type de bien (30%)
        if ($client['type_prefere'] === $bien['type_bien']) {
            $score += 30;
        } elseif (in_array($bien['type_bien'], $this->getTypesSimilaires($client['type_prefere']))) {
            $score += 15;
        }

        // Quartier (20%)
        if ($client['ville_preferee'] === $bien['ville']) {
            $score += 20;
        } elseif ($this->isSameCommune($client['ville_preferee'], $bien['ville'])) {
            $score += 10;
        }

        // Surface (10%)
        if ($client['surface_souhaitee'] > 0 && $bien['surface'] > 0) {
            $diff = abs($bien['surface'] - $client['surface_souhaitee']);
            $tolerance = $client['surface_souhaitee'] * 0.2; // 20% de tolérance
            if ($diff <= $tolerance) {
                $score += 10 * (1 - $diff / $tolerance);
            }
        }

        return min($score, 100.0);
    }

    /**
     * Retourne les top N biens recommandés pour un client
     */
    public function getRecommandations(int $clientId, int $limit = 3): array
    {
        $sql = "SELECT rowid FROM " . $this->db->prefix() . "immo_bien WHERE etat IN ('A_LOUER', 'A_VENDRE')";
        $resql = $this->db->query($sql);

        $scores = [];
        if ($resql) {
            while ($obj = $this->db->fetch_object($resql)) {
                $score = $this->calculerScoreMatching($clientId, (int) $obj->rowid);
                if ($score > 0) {
                    $scores[] = ['bien_id' => (int) $obj->rowid, 'score' => $score];
                }
            }
        }

        // Trier par score décroissant
        usort($scores, fn($a, $b) => $b['score'] <=> $a['score']);
        return array_slice($scores, 0, $limit);
    }

    /**
     * Récupère le profil d'un client (budget, préférences)
     */
    private function getClientProfile(int $clientId): ?array
    {
        $sql = "SELECT budget_max, type_prefere, ville_preferee, surface_souhaitee FROM " . $this->db->prefix() . "immo_client_profile WHERE fk_client = ?";
        // ... implémentation simplifiée
        return null; // Fallback si pas de profil
    }

    /**
     * Types de biens similaires (fallback si pas de match exact)
     */
    private function getTypesSimilaires(string $type): array
    {
        $similaires = [
            'APPART' => ['MAISON'],
            'MAISON' => ['APPART'],
            'BUREAU' => ['BOUTIQUE'],
            'BOUTIQUE' => ['BUREAU'],
        ];
        return $similaires[$type] ?? [];
    }

    /**
     * Vérifie si deux villes sont dans la même commune (approximation)
     */
    private function isSameCommune(string $ville1, string $ville2): bool
    {
        return strcasecmp($ville1, $ville2) === 0;
    }
}
```

---

## 7. Interface utilisateur

### 7.1 Widget Chatbot (widget IA)

Fichier : `mod_immo_ai/class/ai_widget.class.php`

Affichage : Coin inférieur droit de toutes les pages du module Immobilier.

```html
<div id="immo-ai-widget" class="ai-widget-collapsed">
    <div class="ai-widget-header" onclick="toggleAiWidget()">
        <span class="ai-icon">🤖</span>
        <span>Assistant IA</span>
        <span class="ai-status" id="ai-status">●</span>
    </div>
    <div class="ai-widget-body" id="ai-widget-body">
        <div class="ai-messages" id="ai-messages">
            <div class="ai-message ai-bot">
                Bonjour ! Je suis votre assistant immobilier. Posez-moi une question sur vos biens, clients ou le marché.
            </div>
        </div>
        <div class="ai-input-area">
            <input type="text" id="ai-input" placeholder="ex: Quels 3 pièces à Cocody ?" />
            <button onclick="sendAiMessage()">Envoyer</button>
        </div>
    </div>
</div>
```

**Comportement** :
- Clic sur l'entête → expansion/réduction
- Saisie du message + Entrée ou clic Envoyer
- Indicateur de chargement (spinner) pendant la génération
- Réponse affichée avec fond distinct
- Historique conservé pendant la session (pas de persistance DB)

### 7.2 Bouton IA sur fiche bien

Sur `dolibarr-agence-immobien/card.php` :

```html
<div class="tabsAction">
    <a class="butAction" href="card.php?action=edit&id=<?php echo $object->id; ?>">Modifier</a>
    <a class="butAction" href="javascript:generateAiDescription(<?php echo $object->id; ?>)">🤖 Générer description IA</a>
</div>
<div id="ai-description-result" style="display:none;">
    <textarea id="ai-description-text" rows="6" cols="80"></textarea>
    <button onclick="saveAiDescription()">Enregistrer</button>
</div>
```

### 7.3 Onglet Recommandations sur fiche client

Sur `dolibarr-agence-immoclient/card.php`, nouvel onglet **« Recommandations IA »** :

Tableau affichant les 3 biens les plus pertinents avec leur score de matching.

| Bien | Type | Surface | Prix | Score | Action |
|------|------|---------|------|-------|--------|
| B2026-0042 | Appartement | 85 m² | 180 000 FCFA | **92%** | Voir |
| B2026-0038 | Appartement | 78 m² | 165 000 FCFA | **87%** | Voir |
| B2026-0012 | Studio | 45 m² | 120 000 FCFA | **65%** | Voir |

---

## 8. Configuration

### 8.1 Docker Compose (service Ollama)

```yaml
services:
  # ... (db, dolibarr, pgadmin)

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
          memory: 6G
        reservations:
          memory: 4G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  ollama_models:
```

### 8.2 Constantes de configuration (Dolibarr)

| Constante | Défaut | Description |
|-----------|--------|-------------|
| `IMMO_AI_ENABLED` | 0 | Activation du module IA |
| `IMMO_AI_OLLAMA_URL` | `http://ollama:11434` | URL du serveur Ollama |
| `IMMO_AI_MODEL` | `llama3.1:8b` | Modèle LLM utilisé |
| `IMMO_AI_MAX_TOKENS` | 1024 | Limite de tokens par réponse |
| `IMMO_AI_CACHE_TTL` | 3600 | Durée de vie du cache (secondes) |
| `IMMO_AI_TIMEOUT` | 30 | Timeout API (secondes) |

### 8.3 Permissions

| Permission | Description | Module |
|------------|-------------|--------|
| `immo_ai_use` | Utiliser l'assistant IA | immocoreai |
| `immo_ai_admin` | Configurer le module IA (modèle, URL) | immocoreai |

---

## 9. Tests PHPUnit (TDD)

### 9.1 Fichier : `test/phpunit/ImmoAiTest.php`

```php
<?php
declare(strict_types=1);
require_once __DIR__ . '/bootstrap.php';
require_once __DIR__ . '/../../class/immoai.class.php';
require_once __DIR__ . '/../../class/immoaiengine.class.php';

class ImmoAiTest extends PHPUnit\Framework\TestCase
{
    /** @test */
    public function aiClientClassShouldExist(): void
    {
        $this->assertTrue(class_exists('ImmoAiClient'));
    }

    /** @test */
    public function aiEngineClassShouldExist(): void
    {
        $this->assertTrue(class_exists('ImmoAiEngine'));
    }

    /** @test */
    public function aiClientShouldCheckAvailability(): void
    {
        $client = new ImmoAiClient();
        $available = $client->isAvailable();
        $this->assertIsBool($available);
    }

    /** @test */
    public function aiEngineShouldReturnScoreBetweenZeroAndHundred(): void
    {
        $engine = new ImmoAiEngine(new DoliDB());
        $score = $engine->calculerScoreMatching(1, 1);
        $this->assertGreaterThanOrEqual(0.0, $score);
        $this->assertLessThanOrEqual(100.0, $score);
    }

    /** @test */
    public function aiContextShouldBuildBienSearchContext(): void
    {
        $context = new ImmoAiContext(new DoliDB());
        $result = $context->buildContextForBienSearch('Abidjan', 'APPART', 200000);
        $this->assertStringContainsString('Biens disponibles', $result);
    }

    /** @test */
    public function aiSqlTablesShouldExist(): void
    {
        $content = file_get_contents(__DIR__ . '/../../sql/llx_immo_ai.sql');
        $this->assertStringContainsString('CREATE TABLE', $content);
        $this->assertStringContainsString('llx_immo_ai_context', $content);
        $this->assertStringContainsString('llx_immo_ai_logs', $content);
    }

    /** @test */
    public function aiConfigShouldHaveOllamaUrl(): void
    {
        $this->assertEquals('http://ollama:11434', ImmoAiClient::OLLAMA_URL);
    }
}
```

---

## 10. Performance et optimisation

### 10.1 Cache

**Cache table `llx_immo_ai_cache`** :
- Clé : MD5 du prompt complet (question + contexte)
- Valeur : réponse texte
- TTL : 1 heure (configurable)
- Réduction estimée : 60-80% des requêtes sur les questions fréquentes

**Cache fichier PHP** (fallback si PostgreSQL indisponible) :
- Répertoire : `temp/ai_cache/`
- Fichier : `{md5}.json`
- TTL : 1 heure

### 10.2 Limites du contexte RAG

- **Max 10 biens** injectés dans le prompt pour éviter de dépasser la fenêtre de contexte
- **Max 20 comparables** pour les estimations de prix
- **Descriptions tronquées** à 100 caractères dans le contexte

### 10.3 Fallback si Ollama indisponible

1. Vérification `isAvailable()` avant chaque appel
2. Si indisponible : utiliser les recherches SQL classiques + texte fixe
3. Message à l'utilisateur : « L'assistant IA est en maintenance, mode classique activé. »

---

## 11. Notes de développement

- **Jamais de SQL généré par le LLM** — Seul le PHP exécute des requêtes SQL pré-validées
- **Anonymisation systématique** — Les noms de clients, téléphones, adresses exactes ne sont jamais inclus dans les prompts
- **Validation des références** — Tout bien mentionné dans la réponse est vérifié contre la base avant affichage
- **Logs complets** — Chaque interaction est loguée (question, contexte hash, modèle, temps de réponse)
- **Modèle swappable** — Le modèle peut être changé (llama3.1 → mistral → codellama) sans modifier le code métier
- **Testé sur CPU 4 cœurs** — Latence cible < 5 secondes avec Llama 3.1 8B Q4_0

---

*Module mod_immo_ai — Spécification v1.0 | Mai 2026*
