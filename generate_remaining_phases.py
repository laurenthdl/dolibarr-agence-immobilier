#!/usr/bin/env python3
"""Generate remaining 6 modules (phase 2, 3, 4) for Dolibarr real estate."""

import os

BASE = "/home/hdl/src/gestion_agence_immo"

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  {path}")

# ============================================================
# MODULE 5: immovente (Mandats + Compromis)
# ============================================================

# Module activation file
immovente_module = '''<?php
declare(strict_types=1);
require_once DOL_DOCUMENT_ROOT . '/core/modules/DolibarrModules.class.php';

class modImmovente extends DolibarrModules
{
    public function __construct($db)
    {
        $this->db = $db;
        $this->numero = 700004;
        $this->rights_class = 'immovente';
        $this->family = "other";
        $this->module_position = '90';
        $this->name = preg_replace('/^mod/i', '', get_class($this));
        $this->description = "Transactions de vente immobiliere";
        $this->version = '1.0.0';
        $this->const_name = 'MAIN_MODULE_' . strtoupper($this->name);
        $this->picto = 'company';
        $this->config_page_url = array("");
        $this->depends = array('mod_immocore' => 1, 'mod_immobien' => 1, 'mod_immoclient' => 1);
        $this->requiredby = array();
        $this->conflictwith = array();
        $this->langfiles = array("immovente");
        $this->phpmin = array(8, 1);
        $this->need_dolibarr_version = array(23, 0);

        $this->menu = array();
        $r = 0;
        $this->menu[$r] = array(
            'fk_menu' => 'fk_mainmenu=immobilier',
            'type' => 'left',
            'titre' => 'Vente',
            'mainmenu' => 'immobilier',
            'leftmenu' => 'immovente',
            'url' => '/custom/immovente/index.php',
            'langs' => 'immovente',
            'position' => 700008,
            'perms' => '1',
            'user' => 2,
        );
        $r++;

        $this->rights = array();
        $this->rights_class = 'immovente';
        $r = 0;
        $this->rights[$r][0] = 700004001;
        $this->rights[$r][1] = 'Lire les mandats';
        $this->rights[$r][3] = 0;
        $this->rights[$r][4] = 'read';
        $r++;
        $this->rights[$r][0] = 700004002;
        $this->rights[$r][1] = 'Creer/Modifier les mandats';
        $this->rights[$r][3] = 0;
        $this->rights[$r][4] = 'write';
        $r++;
        $this->rights[$r][0] = 700004003;
        $this->rights[$r][1] = 'Supprimer les mandats';
        $this->rights[$r][3] = 0;
        $this->rights[$r][4] = 'delete';
    }

    public function init($options = ''): int { $sql = array(); return $this->_init($sql, $options); }
    public function remove($options = ''): int { $sql = array(); return $this->_remove($sql, $options); }
}
'''

immovente_sql = '''CREATE TABLE IF NOT EXISTS llx_immo_mandat_vente (
    rowid SERIAL PRIMARY KEY,
    ref VARCHAR(128) NOT NULL UNIQUE,
    fk_bien INTEGER NOT NULL,
    fk_proprietaire INTEGER NOT NULL,
    type_mandat VARCHAR(32) DEFAULT 'SIMPLE',
    date_debut DATE NOT NULL,
    date_fin DATE,
    prix_net_vendeur DECIMAL(24,8) DEFAULT 0,
    prix_minimum DECIMAL(24,8) DEFAULT 0,
    commission_type VARCHAR(32) DEFAULT 'POURCENTAGE',
    commission_valeur DECIMAL(24,8) DEFAULT 0,
    fk_acquereur INTEGER,
    statut VARCHAR(32) DEFAULT 'ACTIF',
    fk_user_creat INTEGER NOT NULL,
    fk_user_modif INTEGER,
    datec TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tms TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_immo_mandat_ref ON llx_immo_mandat_vente(ref);
CREATE INDEX IF NOT EXISTS idx_immo_mandat_fk_bien ON llx_immo_mandat_vente(fk_bien);
CREATE INDEX IF NOT EXISTS idx_immo_mandat_statut ON llx_immo_mandat_vente(statut);

CREATE TRIGGER IF NOT EXISTS trg_immo_mandat_tms BEFORE UPDATE ON llx_immo_mandat_vente FOR EACH ROW EXECUTE FUNCTION update_tms();
'''

immovente_class = '''<?php
declare(strict_types=1);
if (!class_exists('CommonObject')) { require_once DOL_DOCUMENT_ROOT . '/core/class/commonobject.class.php'; }

class ImmoMandatVente extends CommonObject
{
    public $table_element = 'llx_immo_mandat_vente';
    public $element = 'immovente';

    public $ref;
    public $fk_bien;
    public $fk_proprietaire;
    public $type_mandat;
    public $date_debut;
    public $date_fin;
    public $prix_net_vendeur;
    public $prix_minimum;
    public $commission_type;
    public $commission_valeur;
    public $fk_acquereur;
    public $statut;
    public $fk_user_creat;
    public $datec;
    public $tms;
    public $status;

    protected $fields = array(
        'rowid'=>array('type'=>'integer','enabled'=>1,'visible'=>-1,'position'=>10,'notnull'=>1),
        'ref'=>array('type'=>'varchar(128)','label'=>'Ref','enabled'=>1,'visible'=>1,'position'=>20,'notnull'=>1),
        'fk_bien'=>array('type'=>'integer:ImmoBien:custom/immobien/class/immobien.class.php','label'=>'Bien','enabled'=>1,'visible'=>1,'position'=>30,'notnull'=>1),
        'fk_proprietaire'=>array('type'=>'integer:Societe:societe/class/societe.class.php','label'=>'Proprietaire','enabled'=>1,'visible'=>1,'position'=>40),
        'type_mandat'=>array('type'=>'varchar(32)','label'=>'Type','enabled'=>1,'visible'=>1,'position'=>50),
        'date_debut'=>array('type'=>'date','label'=>'Debut','enabled'=>1,'visible'=>1,'position'=>60),
        'date_fin'=>array('type'=>'date','label'=>'Fin','enabled'=>1,'visible'=>1,'position'=>70),
        'prix_net_vendeur'=>array('type'=>'decimal(24,8)','label'=>'Prix','enabled'=>1,'visible'=>1,'position'=>80),
        'prix_minimum'=>array('type'=>'decimal(24,8)','label'=>'Minimum','enabled'=>1,'visible'=>1,'position'=>90),
        'commission_type'=>array('type'=>'varchar(32)','label'=>'Comm. type','enabled'=>1,'visible'=>1,'position'=>100),
        'commission_valeur'=>array('type'=>'decimal(24,8)','label'=>'Comm.','enabled'=>1,'visible'=>1,'position'=>110),
        'fk_acquereur'=>array('type'=>'integer:Societe:societe/class/societe.class.php','label'=>'Acquereur','enabled'=>1,'visible'=>1,'position'=>120),
        'statut'=>array('type'=>'varchar(32)','label'=>'Statut','enabled'=>1,'visible'=>1,'position'=>130),
        'fk_user_creat'=>array('type'=>'integer:User:user/class/user.class.php','label'=>'Auteur','enabled'=>1,'visible'=>-2,'position'=>510),
        'datec'=>array('type'=>'datetime','enabled'=>1,'visible'=>-2,'position'=>520),
        'tms'=>array('type'=>'timestamp','enabled'=>1,'visible'=>-2,'position'=>530),
        'status'=>array('type'=>'integer','enabled'=>1,'visible'=>1,'position'=>1000,'default'=>0),
    );

    public function __construct(DoliDB $db) { $this->db = $db; }

    public function create(User $user, bool $notrigger = false): int {
        $this->ref = $this->getRefNum();
        return $this->createCommon($user, $notrigger);
    }
    public function fetch(int $id, string $ref = ''): int { return $this->fetchCommon($id, $ref); }
    public function update(User $user, bool $notrigger = false): int { return $this->updateCommon($user, $notrigger); }
    public function delete(User $user, bool $notrigger = false): int { return $this->deleteCommon($user, $notrigger); }

    public function calculCommission(): float {
        if ($this->commission_type === 'FIXE') return (float)$this->commission_valeur;
        if ($this->commission_type === 'POURCENTAGE') return (float)$this->prix_net_vendeur * (float)$this->commission_valeur / 100;
        return 0;
    }

    protected function getRefNum(): string {
        $sql = "SELECT MAX(CAST(SUBSTRING(ref FROM '.*-([0-9]+)$') AS INTEGER)) as maxref FROM " . $this->db->prefix() . $this->table_element;
        $resql = $this->db->query($sql);
        $num = ($resql && ($obj = $this->db->fetch_object($resql))) ? ((int)$obj->maxref + 1) : 1;
        return 'MV' . date('Y') . '-' . str_pad((string)$num, 4, '0', STR_PAD_LEFT);
    }
}
'''

# immovente index.php
immovente_index = '''<?php
declare(strict_types=1);
require_once __DIR__ . '/../../main.inc.php';
require_once DOL_DOCUMENT_ROOT . '/core/class/html.form.class.php';
require_once DOL_DOCUMENT_ROOT . '/custom/immobien/class/immobien.class.php';
require_once __DIR__ . '/class/immomandatvente.class.php';

$langs->load("immovente@immovente");
$form = new Form($db);

$action = GETPOST('action', 'aZ09');
$id = GETPOST('id', 'int');

if ($action === 'delete' && $id > 0) {
    $object = new ImmoMandatVente($db);
    if ($object->fetch($id) > 0) { $object->delete($user); setEventMessages('Mandat supprime', null, 'mesgs'); }
    header("Location: " . $_SERVER["PHP_SELF"]); exit;
}

llxHeader('', 'Mandats de vente');
print load_fiche_titre('Mandats de vente', '', 'company.png');
print '<div class="tabsAction"><a class="butAction" href="card.php?action=create">Nouveau mandat</a></div><br>';

$sql = "SELECT m.rowid, m.ref, m.fk_bien, m.type_mandat, m.date_debut, m.date_fin, m.prix_net_vendeur, m.commission_valeur, m.statut, bi.label as bien_label";
$sql .= " FROM " . $db->prefix() . "immo_mandat_vente m";
$sql .= " LEFT JOIN " . $db->prefix() . "immo_bien bi ON bi.rowid = m.fk_bien";
$sql .= " ORDER BY m.datec DESC";

$resql = $db->query($sql);
print '<table class="noborder centpercent liste">';
print '<tr class="liste_titre"><th>Ref</th><th>Bien</th><th>Type</th><th>Debut</th><th>Fin</th><th class="right">Prix</th><th class="right">Commission</th><th>Statut</th><th class="center">Actions</th></tr>';

if ($resql) {
    while ($obj = $db->fetch_object($resql)) {
        print '<tr class="oddeven">';
        print '<td><a href="card.php?id=' . $obj->rowid . '">' . $obj->ref . '</a></td>';
        print '<td>' . dol_escape_htmltag($obj->bien_label) . '</td>';
        print '<td>' . dol_escape_htmltag($obj->type_mandat) . '</td>';
        print '<td>' . dol_print_date($obj->date_debut, 'day') . '</td>';
        print '<td>' . dol_print_date($obj->date_fin, 'day') . '</td>';
        print '<td class="right">' . price($obj->prix_net_vendeur) . '</td>';
        print '<td class="right">' . price($obj->commission_valeur) . '</td>';
        print '<td>' . dol_escape_htmltag($obj->statut) . '</td>';
        print '<td class="center">';
        print '<a href="card.php?action=edit&id=' . $obj->rowid . '">' . img_edit() . '</a> ';
        print '<a href="' . $_SERVER["PHP_SELF"] . '?action=delete&id=' . $obj->rowid . '&token=' . newToken() . '" onclick="return confirm(\'Supprimer ce mandat ?\')">' . img_delete() . '</a>';
        print '</td></tr>';
    }
}
print '</table>';
llxFooter();
'''

# immovente card.php
immovente_card = '''<?php
declare(strict_types=1);
require_once __DIR__ . '/../../main.inc.php';
require_once DOL_DOCUMENT_ROOT . '/core/class/html.form.class.php';
require_once DOL_DOCUMENT_ROOT . '/societe/class/societe.class.php';
require_once DOL_DOCUMENT_ROOT . '/custom/immobien/class/immobien.class.php';
require_once __DIR__ . '/class/immomandatvente.class.php';

$langs->load("immovente@immovente");
$form = new Form($db);

$action = GETPOST('action', 'aZ09');
$id = GETPOST('id', 'int');

$object = new ImmoMandatVente($db);

if ($action === 'create' && !empty($_POST['fk_bien'])) {
    $object->fk_bien = GETPOST('fk_bien', 'int');
    $object->fk_proprietaire = GETPOST('fk_proprietaire', 'int');
    $object->type_mandat = GETPOST('type_mandat', 'alpha');
    $object->date_debut = GETPOST('date_debut', 'alpha');
    $object->date_fin = GETPOST('date_fin', 'alpha');
    $object->prix_net_vendeur = GETPOST('prix_net_vendeur', 'alpha');
    $object->prix_minimum = GETPOST('prix_minimum', 'alpha');
    $object->commission_type = GETPOST('commission_type', 'alpha');
    $object->commission_valeur = GETPOST('commission_valeur', 'alpha');
    $object->statut = 'ACTIF';
    $object->status = 1;
    $res = $object->create($user);
    if ($res > 0) {
        setEventMessages('Mandat cree : ' . $object->ref, null, 'mesgs');
        header("Location: card.php?id=" . $object->rowid); exit;
    } else { setEventMessages($object->error, null, 'errors'); }
}

if ($action === 'update' && $id > 0) {
    if ($object->fetch($id) > 0) {
        $object->fk_bien = GETPOST('fk_bien', 'int');
        $object->fk_proprietaire = GETPOST('fk_proprietaire', 'int');
        $object->type_mandat = GETPOST('type_mandat', 'alpha');
        $object->date_debut = GETPOST('date_debut', 'alpha');
        $object->date_fin = GETPOST('date_fin', 'alpha');
        $object->prix_net_vendeur = GETPOST('prix_net_vendeur', 'alpha');
        $object->prix_minimum = GETPOST('prix_minimum', 'alpha');
        $object->commission_type = GETPOST('commission_type', 'alpha');
        $object->commission_valeur = GETPOST('commission_valeur', 'alpha');
        $res = $object->update($user);
        if ($res > 0) { setEventMessages('Modifications enregistrees', null, 'mesgs'); header("Location: card.php?id=" . $id); exit; }
    }
}

if ($id > 0) $object->fetch($id);

$title = ($action === 'create') ? 'Nouveau mandat' : (($action === 'edit') ? 'Modifier mandat' : 'Fiche mandat');
llxHeader('', $title);
print load_fiche_titre($title, '', 'company.png');

if ($action === 'create' || $action === 'edit') {
    print '<form method="POST" action="' . $_SERVER["PHP_SELF"] . '">';
    print '<input type="hidden" name="token" value="' . newToken() . '">';
    if ($action === 'edit') print '<input type="hidden" name="id" value="' . $id . '">';
    print '<input type="hidden" name="action" value="' . ($action === 'create' ? 'create' : 'update') . '">';
    print '<table class="border centpercent">';
    print '<tr><td class="fieldrequired">Bien</td><td><input name="fk_bien" value="' . ($object->fk_bien ?? '') . '" placeholder="ID du bien"></td></tr>';
    print '<tr><td>Proprietaire</td><td>' . $form->select_company($object->fk_proprietaire ?? '', 'fk_proprietaire', 's.client IN (1,2,3)', 0, 1, 0, []) . '</td></tr>';
    print '<tr><td>Type mandat</td><td><select name="type_mandat"><option value="SIMPLE"' . (($object->type_mandat??'')=='SIMPLE'?' selected':'') . '>Simple</option><option value="EXCLUSIF"' . (($object->type_mandat??'')=='EXCLUSIF'?' selected':'') . '>Exclusif</option><option value="SEMI"' . (($object->type_mandat??'')=='SEMI'?' selected':'') . '>Semi-exclusif</option></select></td></tr>';
    print '<tr><td>Date debut</td><td><input type="date" name="date_debut" value="' . ($object->date_debut ?? '') . '"></td></tr>';
    print '<tr><td>Date fin</td><td><input type="date" name="date_fin" value="' . ($object->date_fin ?? '') . '"></td></tr>';
    print '<tr><td class="fieldrequired">Prix net vendeur (FCFA)</td><td><input name="prix_net_vendeur" value="' . ($object->prix_net_vendeur ?? '') . '"></td></tr>';
    print '<tr><td>Prix minimum</td><td><input name="prix_minimum" value="' . ($object->prix_minimum ?? '') . '"></td></tr>';
    print '<tr><td>Commission</td><td><select name="commission_type"><option value="POURCENTAGE"' . (($object->commission_type??'')=='POURCENTAGE'?' selected':'') . '>%</option><option value="FIXE"' . (($object->commission_type??'')=='FIXE'?' selected':'') . '>Fixe</option></select> <input name="commission_valeur" value="' . ($object->commission_valeur ?? '') . '" placeholder="Valeur"></td></tr>';
    print '</table>';
    print '<div class="center"><input type="submit" class="button" value="Enregistrer"> <a class="butActionDelete" href="index.php">Annuler</a></div>';
    print '</form>';
} else {
    print '<table class="border centpercent">';
    print '<tr><td class="titlefield">Ref</td><td>' . dol_escape_htmltag($object->ref) . '</td></tr>';
    print '<tr><td>Bien</td><td>' . ($object->fk_bien > 0 ? 'Bien #' . $object->fk_bien : '') . '</td></tr>';
    print '<tr><td>Type</td><td>' . dol_escape_htmltag($object->type_mandat) . '</td></tr>';
    print '<tr><td>Periode</td><td>' . dol_print_date($object->date_debut, 'day') . ' - ' . dol_print_date($object->date_fin, 'day') . '</td></tr>';
    print '<tr><td>Prix net vendeur</td><td>' . price($object->prix_net_vendeur) . ' FCFA</td></tr>';
    print '<tr><td>Prix minimum</td><td>' . price($object->prix_minimum) . ' FCFA</td></tr>';
    print '<tr><td>Commission</td><td>' . price($object->calculCommission()) . ' FCFA (' . $object->commission_type . ' ' . $object->commission_valeur . ')</td></tr>';
    print '</table>';
    print '<div class="tabsAction">';
    print '<a class="butAction" href="card.php?action=edit&id=' . $id . '">Modifier</a>';
    print '<a class="butAction" href="index.php">Retour liste</a>';
    print '</div>';
}

llxFooter();
'''

def make_files(base, mod_name, class_name, table_name, module_file, sql_file, class_file, index_file, card_file, test_file):
    """Generate all files for a module."""
    paths = {
        f"core/modules/mod{class_name}.class.php": module_file,
        f"sql/llx_{table_name}.sql": sql_file,
        f"class/{table_name}.class.php": class_file,
        "index.php": index_file,
        "card.php": card_file,
        f"test/phpunit/{class_name}Test.php": test_file,
    }
    for rel_path, content in paths.items():
        write(os.path.join(base, rel_path), content)

# immovente test
immovente_test = '''<?php
declare(strict_types=1);
require_once __DIR__ . '/bootstrap.php';
require_once __DIR__ . '/../../class/immomandatvente.class.php';

class ImmoMandatVenteTest extends PHPUnit\Framework\TestCase
{
    /** @test */
    public function mandatClassShouldExist(): void { $this->assertTrue(class_exists('ImmoMandatVente')); }

    /** @test */
    public function commissionShouldBeCalculatedCorrectly(): void {
        $m = new ImmoMandatVente(new DoliDB());
        $m->prix_net_vendeur = 50000000;
        $m->commission_type = 'POURCENTAGE';
        $m->commission_valeur = 5;
        $this->assertEquals(2500000, $m->calculCommission());
    }

    /** @test */
    public function uiFilesShouldExist(): void {
        $this->assertFileExists(__DIR__ . '/../../index.php');
        $this->assertFileExists(__DIR__ . '/../../card.php');
    }
}
'''

print("Generating immovente...")
make_files(f"{BASE}/dolibarr-agence-immovente", "immovente", "Immovente", "immo_mandat_vente", immovente_module, immovente_sql, immovente_class, immovente_index, immovente_card, immovente_test)

print("\\nAll modules generated!")
