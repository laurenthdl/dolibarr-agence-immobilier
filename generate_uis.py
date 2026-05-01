#!/usr/bin/env python3
"""Generate all module UI files for Dolibarr real estate modules."""
import os

BASE = "/home/hdl/src/gestion_agence_immo"

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  Written: {os.path.basename(os.path.dirname(path))}/{os.path.basename(path)}")

# Module 1: immocore
write_file(os.path.join(BASE, "dolibarr-agence-immocore", "index.php"), '''<?php
declare(strict_types=1);
require_once __DIR__ . '/../../main.inc.php';
require_once DOL_DOCUMENT_ROOT . '/core/lib/admin.lib.php';
$langs->load("immocore@immocore");
if (!$user->admin) accessforbidden();

$action = GETPOST('action', 'aZ09');
if ($action === 'save') {
    $mods = GETPOST('modules', 'array');
    $all = ['immobien','immoclient','immolocatif','immovente','immoreno','immosyndic','immomarche','immodjamo','immorapports'];
    foreach ($all as $m) {
        $v = in_array($m, $mods) ? '1' : '0';
        dolibarr_set_const($db, 'IMMO_ACTIVATE_' . strtoupper($m), $v, 'chaine', 0, '', $conf->entity);
    }
    setEventMessages($langs->trans("SetupSaved"), null, 'mesgs');
    header("Location: " . $_SERVER["PHP_SELF"]); exit;
}

llxHeader('', 'Configuration Immobilier');
print load_fiche_titre('Configuration Immobilier', '', 'title_setup.png');
print '<form method="POST">';
print '<input type="hidden" name="token" value="' . newToken() . '">';
print '<input type="hidden" name="action" value="save">';
print '<table class="noborder centpercent">';
print '<tr class="liste_titre"><td>Module</td><td class="center">Activer</td></tr>';
$modules = ['immobien'=>'Biens','immoclient'=>'Clients','immolocatif'=>'Location','immovente'=>'Vente','immoreno'=>'Renovation','immosyndic'=>'Syndic','immomarche'=>'Etude de marche','immodjamo'=>'Paiement Djamo','immorapports'=>'Rapports'];
foreach ($modules as $k=>$l) {
    $active = !empty($conf->global->{'IMMO_ACTIVATE_' . strtoupper($k)});
    print '<tr class="oddeven"><td>' . $l . '</td><td class="center"><input type="checkbox" name="modules[]" value="' . $k . '"' . ($active?' checked':'') . '></td></tr>';
}
print '</table>';
print '<div class="center"><input type="submit" class="button" value="Enregistrer"></div>';
print '</form>';
llxFooter();
''')

# Module 2: immobien - class and SQL
write_file(os.path.join(BASE, "dolibarr-agence-immobien", "class", "immobien.class.php"), '''<?php
declare(strict_types=1);
require_once DOL_DOCUMENT_ROOT . '/core/class/commonobject.class.php';

class ImmoBien extends CommonObject
{
    public $table_element = 'llx_immo_bien';
    public $element = 'immobien';

    public $ref;
    public $label;
    public $fk_soc_proprietaire;
    public $type_bien;
    public $etat;
    public $adresse;
    public $cp;
    public $ville;
    public $pays;
    public $superficie_habitable;
    public $nombre_pieces;
    public $description;
    public $prix_location;
    public $prix_vente;
    public $fk_user_creat;
    public $datec;
    public $tms;
    public $status;

    protected $fields = array(
        'rowid'=>array('type'=>'integer','label'=>'ID','enabled'=>1,'visible'=>-1,'position'=>10,'notnull'=>1),
        'ref'=>array('type'=>'varchar(128)','label'=>'Ref','enabled'=>1,'visible'=>1,'position'=>20,'notnull'=>1,'searchall'=>1),
        'label'=>array('type'=>'varchar(255)','label'=>'Libelle','enabled'=>1,'visible'=>1,'position'=>30,'notnull'=>1,'searchall'=>1),
        'fk_soc_proprietaire'=>array('type'=>'integer:Societe:societe/class/societe.class.php','label'=>'Proprietaire','enabled'=>1,'visible'=>1,'position'=>40),
        'type_bien'=>array('type'=>'varchar(64)','label'=>'Type','enabled'=>1,'visible'=>1,'position'=>50),
        'etat'=>array('type'=>'varchar(32)','label'=>'Etat','enabled'=>1,'visible'=>1,'position'=>60),
        'adresse'=>array('type'=>'varchar(255)','label'=>'Adresse','enabled'=>1,'visible'=>1,'position'=>70),
        'cp'=>array('type'=>'varchar(32)','label'=>'CP','enabled'=>1,'visible'=>1,'position'=>80),
        'ville'=>array('type'=>'varchar(128)','label'=>'Ville','enabled'=>1,'visible'=>1,'position'=>90),
        'pays'=>array('type'=>'varchar(2)','label'=>'Pays','enabled'=>1,'visible'=>-1,'position'=>100),
        'superficie_habitable'=>array('type'=>'decimal(24,8)','label'=>'Surface','enabled'=>1,'visible'=>1,'position'=>130),
        'nombre_pieces'=>array('type'=>'integer','label'=>'Pieces','enabled'=>1,'visible'=>1,'position'=>150),
        'description'=>array('type'=>'text','label'=>'Description','enabled'=>1,'visible'=>1,'position'=>190),
        'prix_location'=>array('type'=>'decimal(24,8)','label'=>'Loyer','enabled'=>1,'visible'=>1,'position'=>210),
        'prix_vente'=>array('type'=>'decimal(24,8)','label'=>'Prix vente','enabled'=>1,'visible'=>1,'position'=>220),
        'fk_user_creat'=>array('type'=>'integer:User:user/class/user.class.php','label'=>'Auteur','enabled'=>1,'visible'=>-2,'position'=>510),
        'datec'=>array('type'=>'datetime','label'=>'DateCreation','enabled'=>1,'visible'=>-2,'position'=>530),
        'tms'=>array('type'=>'timestamp','label'=>'DateModif','enabled'=>1,'visible'=>-2,'position'=>540),
        'status'=>array('type'=>'integer','label'=>'Status','enabled'=>1,'visible'=>1,'position'=>1000,'default'=>0),
    );

    public function __construct(DoliDB $db) { $this->db = $db; }

    public function create(User $user, bool $notrigger = false): int {
        $this->ref = $this->getRefNum();
        return $this->createCommon($user, $notrigger);
    }
    public function fetch(int $id, string $ref = ''): int { return $this->fetchCommon($id, $ref); }
    public function update(User $user, bool $notrigger = false): int { return $this->updateCommon($user, $notrigger); }
    public function delete(User $user, bool $notrigger = false): int { return $this->deleteCommon($user, $notrigger); }

    protected function getRefNum(): string {
        $sql = "SELECT MAX(CAST(SUBSTRING(ref FROM '.*-([0-9]+)$') AS INTEGER)) as maxref FROM " . $this->db->prefix() . $this->table_element;
        $resql = $this->db->query($sql);
        $num = ($resql && ($obj = $this->db->fetch_object($resql))) ? ((int)$obj->maxref + 1) : 1;
        return 'B' . date('Y') . '-' . str_pad((string)$num, 4, '0', STR_PAD_LEFT);
    }
}
''')

write_file(os.path.join(BASE, "dolibarr-agence-immobien", "sql", "llx_immo_bien.sql"), '''CREATE TABLE IF NOT EXISTS llx_immo_bien (
    rowid SERIAL PRIMARY KEY,
    ref VARCHAR(128) NOT NULL UNIQUE,
    label VARCHAR(255) NOT NULL,
    fk_soc_proprietaire INTEGER,
    type_bien VARCHAR(64),
    etat VARCHAR(32) DEFAULT 'A_ACQUERIR',
    adresse VARCHAR(255),
    cp VARCHAR(32),
    ville VARCHAR(128),
    pays VARCHAR(2) DEFAULT 'CI',
    superficie_habitable DECIMAL(24,8),
    nombre_pieces INTEGER,
    description TEXT,
    prix_location DECIMAL(24,8),
    prix_vente DECIMAL(24,8),
    fk_user_creat INTEGER NOT NULL,
    datec TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tms TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_immo_bien_ref ON llx_immo_bien(ref);
CREATE INDEX IF NOT EXISTS idx_immo_bien_ville ON llx_immo_bien(ville);

CREATE OR REPLACE FUNCTION update_tms() RETURNS TRIGGER AS $$ BEGIN NEW.tms = CURRENT_TIMESTAMP; RETURN NEW; END; $$ LANGUAGE plpgsql;
DROP TRIGGER IF EXISTS trg_immo_bien_tms ON llx_immo_bien;
CREATE TRIGGER trg_immo_bien_tms BEFORE UPDATE ON llx_immo_bien FOR EACH ROW EXECUTE FUNCTION update_tms();
''')

# Module 2: immobien - UI
write_file(os.path.join(BASE, "dolibarr-agence-immobien", "index.php"), '''<?php
declare(strict_types=1);
require_once __DIR__ . '/../../main.inc.php';
require_once DOL_DOCUMENT_ROOT . '/core/class/html.form.class.php';
require_once __DIR__ . '/class/immobien.class.php';

$langs->load("immobien@immobien");
$action = GETPOST('action', 'aZ09');
$id = GETPOST('id', 'int');

if ($action === 'delete' && $id > 0) {
    $object = new ImmoBien($db);
    if ($object->fetch($id) > 0) { $object->delete($user); setEventMessages('Bien supprime', null, 'mesgs'); }
    header("Location: " . $_SERVER["PHP_SELF"]); exit;
}

llxHeader('', 'Biens immobiliers');
print load_fiche_titre('Biens immobiliers', '', 'company.png');
print '<div class="tabsAction"><a class="butAction" href="card.php?action=create">Nouveau bien</a></div><br>';

$sql = "SELECT rowid, ref, label, type_bien, etat, ville, superficie_habitable, prix_location, prix_vente FROM " . $db->prefix() . "immo_bien ORDER BY datec DESC";
$resql = $db->query($sql);

print '<table class="noborder centpercent liste">';
print '<tr class="liste_titre"><th>Ref</th><th>Libelle</th><th>Type</th><th>Etat</th><th>Ville</th><th class="right">Surface</th><th class="right">Location</th><th class="right">Vente</th><th class="center">Actions</th></tr>';

if ($resql) {
    while ($obj = $db->fetch_object($resql)) {
        print '<tr class="oddeven">';
        print '<td><a href="card.php?id=' . $obj->rowid . '">' . $obj->ref . '</a></td>';
        print '<td>' . dol_escape_htmltag($obj->label) . '</td>';
        print '<td>' . dol_escape_htmltag($obj->type_bien) . '</td>';
        print '<td>' . dol_escape_htmltag($obj->etat) . '</td>';
        print '<td>' . dol_escape_htmltag($obj->ville) . '</td>';
        print '<td class="right">' . price($obj->superficie_habitable) . ' m<sup>2</sup></td>';
        print '<td class="right">' . price($obj->prix_location) . '</td>';
        print '<td class="right">' . price($obj->prix_vente) . '</td>';
        print '<td class="center">';
        print '<a href="card.php?action=edit&id=' . $obj->rowid . '">' . img_edit() . '</a> ';
        print '<a href="' . $_SERVER["PHP_SELF"] . '?action=delete&id=' . $obj->rowid . '&token=' . newToken() . '" onclick="return confirm(\'Supprimer ce bien ?\')">' . img_delete() . '</a>';
        print '</td></tr>';
    }
}
print '</table>';
llxFooter();
''')

write_file(os.path.join(BASE, "dolibarr-agence-immobien", "card.php"), '''<?php
declare(strict_types=1);
require_once __DIR__ . '/../../main.inc.php';
require_once DOL_DOCUMENT_ROOT . '/core/class/html.form.class.php';
require_once DOL_DOCUMENT_ROOT . '/societe/class/societe.class.php';
require_once __DIR__ . '/class/immobien.class.php';

$langs->load("immobien@immobien");
$form = new Form($db);

$action = GETPOST('action', 'aZ09');
$id = GETPOST('id', 'int');
$object = new ImmoBien($db);

if ($action === 'create' && !empty($_POST['label'])) {
    $object->label = GETPOST('label', 'alpha');
    $object->type_bien = GETPOST('type_bien', 'alpha');
    $object->etat = GETPOST('etat', 'alpha');
    $object->adresse = GETPOST('adresse', 'alpha');
    $object->cp = GETPOST('cp', 'alpha');
    $object->ville = GETPOST('ville', 'alpha');
    $object->superficie_habitable = GETPOST('superficie_habitable', 'alpha');
    $object->nombre_pieces = GETPOST('nombre_pieces', 'int');
    $object->description = GETPOST('description', 'none');
    $object->prix_location = GETPOST('prix_location', 'alpha');
    $object->prix_vente = GETPOST('prix_vente', 'alpha');
    $object->fk_soc_proprietaire = GETPOST('fk_soc_proprietaire', 'int');
    $object->status = 1;
    $res = $object->create($user);
    if ($res > 0) { setEventMessages('Bien cree : ' . $object->ref, null, 'mesgs'); header("Location: card.php?id=" . $object->rowid); exit; }
    else { setEventMessages($object->error, null, 'errors'); }
}

if ($action === 'update' && $id > 0) {
    if ($object->fetch($id) > 0) {
        $object->label = GETPOST('label', 'alpha');
        $object->type_bien = GETPOST('type_bien', 'alpha');
        $object->etat = GETPOST('etat', 'alpha');
        $object->adresse = GETPOST('adresse', 'alpha');
        $object->ville = GETPOST('ville', 'alpha');
        $object->superficie_habitable = GETPOST('superficie_habitable', 'alpha');
        $object->nombre_pieces = GETPOST('nombre_pieces', 'int');
        $object->description = GETPOST('description', 'none');
        $object->prix_location = GETPOST('prix_location', 'alpha');
        $object->prix_vente = GETPOST('prix_vente', 'alpha');
        $object->fk_soc_proprietaire = GETPOST('fk_soc_proprietaire', 'int');
        $res = $object->update($user);
        if ($res > 0) { setEventMessages('Modifications enregistrees', null, 'mesgs'); header("Location: card.php?id=" . $id); exit; }
    }
}

if ($id > 0) $object->fetch($id);

$title = ($action === 'create') ? 'Nouveau bien' : (($action === 'edit') ? 'Modifier bien' : 'Fiche bien');
llxHeader('', $title);
print load_fiche_titre($title, '', 'company.png');

if ($action === 'create' || $action === 'edit') {
    print '<form method="POST" action="' . $_SERVER["PHP_SELF"] . '">';
    print '<input type="hidden" name="token" value="' . newToken() . '">';
    if ($action === 'edit') print '<input type="hidden" name="id" value="' . $id . '">';
    print '<input type="hidden" name="action" value="' . ($action === 'create' ? 'create' : 'update') . '">';
    print '<table class="border centpercent">';
    print '<tr><td class="fieldrequired">Libelle</td><td><input name="label" value="' . dol_escape_htmltag($object->label ?? '') . '" class="minwidth300"></td></tr>';
    print '<tr><td>Type</td><td><input name="type_bien" value="' . dol_escape_htmltag($object->type_bien ?? '') . '" placeholder="Maison, Appartement..."></td></tr>';
    print '<tr><td>Etat</td><td><select name="etat"><option value="DISPONIBLE"' . (($object->etat??'')=='DISPONIBLE'?' selected':'') . '>Disponible</option><option value="A_LOUER"' . (($object->etat??'')=='A_LOUER'?' selected':'') . '>A louer</option><option value="A_VENDRE"' . (($object->etat??'')=='A_VENDRE'?' selected':'') . '>A vendre</option><option value="LOUE"' . (($object->etat??'')=='LOUE'?' selected':'') . '>Loue</option><option value="VENDU"' . (($object->etat??'')=='VENDU'?' selected':'') . '>Vendu</option></select></td></tr>';
    print '<tr><td>Adresse</td><td><input name="adresse" value="' . dol_escape_htmltag($object->adresse ?? '') . '" class="minwidth300"></td></tr>';
    print '<tr><td>Ville</td><td><input name="ville" value="' . dol_escape_htmltag($object->ville ?? '') . '"></td></tr>';
    print '<tr><td>Surface habitable (m2)</td><td><input name="superficie_habitable" value="' . ($object->superficie_habitable ?? '') . '"></td></tr>';
    print '<tr><td>Nb pieces</td><td><input name="nombre_pieces" value="' . ($object->nombre_pieces ?? '') . '"></td></tr>';
    print '<tr><td>Proprietaire</td><td>' . $form->select_company($object->fk_soc_proprietaire ?? '', 'fk_soc_proprietaire', '1', 0, 1, 0, []) . '</td></tr>';
    print '<tr><td>Prix location (FCFA)</td><td><input name="prix_location" value="' . ($object->prix_location ?? '') . '"></td></tr>';
    print '<tr><td>Prix vente (FCFA)</td><td><input name="prix_vente" value="' . ($object->prix_vente ?? '') . '"></td></tr>';
    print '<tr><td>Description</td><td><textarea name="description" rows="3" class="quatrevingtpercent">' . dol_escape_htmltag($object->description ?? '') . '</textarea></td></tr>';
    print '</table>';
    print '<div class="center"><input type="submit" class="button" value="Enregistrer"> <a class="butActionDelete" href="index.php">Annuler</a></div>';
    print '</form>';
} else {
    print '<table class="border centpercent">';
    print '<tr><td class="titlefield">Ref</td><td>' . dol_escape_htmltag($object->ref) . '</td></tr>';
    print '<tr><td>Libelle</td><td>' . dol_escape_htmltag($object->label) . '</td></tr>';
    print '<tr><td>Type</td><td>' . dol_escape_htmltag($object->type_bien) . '</td></tr>';
    print '<tr><td>Etat</td><td>' . dol_escape_htmltag($object->etat) . '</td></tr>';
    print '<tr><td>Adresse</td><td>' . dol_escape_htmltag($object->adresse) . ' - ' . dol_escape_htmltag($object->ville) . '</td></tr>';
    print '<tr><td>Surface</td><td>' . price($object->superficie_habitable) . ' m<sup>2</sup></td></tr>';
    print '<tr><td>Prix location</td><td>' . price($object->prix_location) . ' FCFA</td></tr>';
    print '<tr><td>Prix vente</td><td>' . price($object->prix_vente) . ' FCFA</td></tr>';
    print '<tr><td>Description</td><td>' . nl2br(dol_escape_htmltag($object->description)) . '</td></tr>';
    print '</table>';
    print '<div class="tabsAction">';
    print '<a class="butAction" href="card.php?action=edit&id=' . $id . '">Modifier</a>';
    print '<a class="butAction" href="index.php">Retour liste</a>';
    print '</div>';
}
llxFooter();
''')

# Module 3: immoclient
write_file(os.path.join(BASE, "dolibarr-agence-immoclient", "index.php"), '''<?php
declare(strict_types=1);
require_once __DIR__ . '/../../main.inc.php';
require_once DOL_DOCUMENT_ROOT . '/societe/class/societe.class.php';

$langs->load("immoclient@immoclient");
llxHeader('', 'Clients immobiliers');
print load_fiche_titre('Clients immobiliers', '', 'company.png');
print '<div class="tabsAction"><a class="butAction" href="' . DOL_URL_ROOT . '/societe/card.php?action=create&type=t">Nouveau client</a></div><br>';

$sql = "SELECT s.rowid, s.nom, s.email, s.phone, s.town FROM " . $db->prefix() . "societe s WHERE s.client IN (1,2,3) ORDER BY s.nom";
$resql = $db->query($sql);
print '<table class="noborder centpercent liste"><tr class="liste_titre"><th>Nom</th><th>Email</th><th>Telephone</th><th>Ville</th><th class="center">Actions</th></tr>';
if ($resql) {
    while ($obj = $db->fetch_object($resql)) {
        print '<tr class="oddeven">';
        print '<td><a href="card.php?id=' . $obj->rowid . '">' . dol_escape_htmltag($obj->nom) . '</a></td>';
        print '<td>' . dol_escape_htmltag($obj->email) . '</td>';
        print '<td>' . dol_escape_htmltag($obj->phone) . '</td>';
        print '<td>' . dol_escape_htmltag($obj->town) . '</td>';
        print '<td class="center"><a href="card.php?id=' . $obj->rowid . '">' . img_picto('Voir', 'view') . '</a></td>';
        print '</tr>';
    }
}
print '</table>';
llxFooter();
''')

write_file(os.path.join(BASE, "dolibarr-agence-immoclient", "card.php"), '''<?php
declare(strict_types=1);
require_once __DIR__ . '/../../main.inc.php';
require_once DOL_DOCUMENT_ROOT . '/societe/class/societe.class.php';

$langs->load("immoclient@immoclient");
$id = GETPOST('id', 'int');
$object = new Societe($db);
if ($id > 0) $object->fetch($id);

llxHeader('', 'Fiche client');
print load_fiche_titre('Fiche client : ' . dol_escape_htmltag($object->nom), '', 'company.png');
print '<table class="border centpercent">';
print '<tr><td class="titlefield">Nom</td><td>' . dol_escape_htmltag($object->nom) . '</td></tr>';
print '<tr><td>Email</td><td>' . dol_escape_htmltag($object->email) . '</td></tr>';
print '<tr><td>Telephone</td><td>' . dol_escape_htmltag($object->phone) . '</td></tr>';
print '<tr><td>Adresse</td><td>' . dol_escape_htmltag($object->address) . ', ' . dol_escape_htmltag($object->town) . '</td></tr>';
print '<tr><td>Type</td><td>' . $object->getTypeUrl(2) . '</td></tr>';
print '</table>';
print '<div class="tabsAction">';
print '<a class="butAction" href="' . DOL_URL_ROOT . '/societe/card.php?socid=' . $id . '&action=edit">Modifier dans Dolibarr</a>';
print '<a class="butAction" href="index.php">Retour liste</a>';
print '</div>';
llxFooter();
''')

# Module 4 & 5: placeholder
placeholder = '''<?php
declare(strict_types=1);
require_once __DIR__ . '/../../main.inc.php';
llxHeader('', 'Module en cours de developpement');
print '<div class="info">Ce module sera implemente dans la prochaine phase de developpement.</div>';
llxFooter();
'''

for mod in ["dolibarr-agence-immolocatif", "dolibarr-agence-immovente"]:
    write_file(os.path.join(BASE, mod, "index.php"), placeholder)
    write_file(os.path.join(BASE, mod, "card.php"), placeholder)

print("All UIs generated successfully!")
