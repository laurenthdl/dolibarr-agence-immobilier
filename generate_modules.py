#!/usr/bin/env python3
"""Generate all 5 Dolibarr modules with complete structure, tests, and GitHub Actions."""

import os
import subprocess

BASE_DIR = "/home/hdl/src/gestion_agence_immo"

MODULES = {
    "immocore": {
        "numero": 700000,
        "class_name": "modImmocore",
        "object_name": "ImmoCoreConfig",
        "table": "immo_config",
        "depends": [],
        "label": "Immobilier - Core",
        "description": "Module de base pour la gestion immobilière",
    },
    "immobien": {
        "numero": 700001,
        "class_name": "modImmobien",
        "object_name": "ImmoBien",
        "table": "immo_bien",
        "depends": ["immocore", "societe"],
        "label": "Immobilier - Biens",
        "description": "Gestion des biens immobiliers",
    },
    "immoclient": {
        "numero": 700002,
        "class_name": "modImmoclient",
        "object_name": "ImmoClientType",
        "table": "immo_client_type",
        "depends": ["immocore", "societe"],
        "label": "Immobilier - Clients",
        "description": "CRM immobilier et visites",
    },
    "immolocatif": {
        "numero": 700003,
        "class_name": "modImmolocatif",
        "object_name": "ImmoBail",
        "table": "immo_bail",
        "depends": ["immocore", "immobien", "immoclient", "societe"],
        "label": "Immobilier - Location",
        "description": "Gestion locative et quittances",
    },
    "immovente": {
        "numero": 700004,
        "class_name": "modImmovente",
        "object_name": "ImmoMandatVente",
        "table": "immo_mandat_vente",
        "depends": ["immocore", "immobien", "immoclient", "societe"],
        "label": "Immobilier - Vente",
        "description": "Transactions de vente immobilière",
    },
}


def write_file(path: str, content: str):
    """Write file with content."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"✓ Created {path}")


def generate_gitignore(module_dir: str):
    write_file(
        os.path.join(module_dir, ".gitignore"),
        """# Build artifacts
/build/
/vendor/
/composer.lock

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Test coverage
/coverage/
*.cov

# Dolibarr specific
*.lock
/documents/
""",
    )


def generate_github_actions(module_dir: str, module_name: str):
    yml = f"""name: Tests {module_name}

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        php-version: ['8.2', '8.4']

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: dolibarr_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v4

    - name: Setup PHP
      uses: shivammathur/setup-php@v2
      with:
        php-version: ${{ matrix.php-version }}
        extensions: pdo, pdo_pgsql, mbstring, json
        coverage: xdebug

    - name: Validate composer.json
      run: composer validate --strict || true

    - name: Install dependencies
      run: |
        if [ -f composer.json ]; then composer install --prefer-dist --no-progress; fi

    - name: Run PHPUnit tests
      run: |
        if [ -f test/phpunit/{module_name.capitalize()}Test.php ]; then
          php test/phpunit/{module_name.capitalize()}Test.php
        fi
      env:
        DB_TYPE: pgsql
        DB_HOST: localhost
        DB_PORT: 5432
        DB_NAME: dolibarr_test
        DB_USER: postgres
        DB_PASS: postgres

    - name: Run PHP syntax check
      run: find . -name "*.php" -not -path "./vendor/*" -exec php -l {{}} \;
"""
    write_file(os.path.join(module_dir, ".github", "workflows", "tests.yml"), yml)


def generate_module_class(module_dir: str, info: dict, module_name: str):
    depends_str = ", ".join([f"'mod_{d}' => 1" for d in info["depends"]])
    dependances_str = "\n        \n".join(
        [f"require_once DOL_DOCUMENT_ROOT . '/custom/{d}/core/modules/mod{d}.class.php';" for d in info["depends"] if d.startswith("immo")]
    )
    
    content = f"""<?php

declare(strict_types=1);

require_once DOL_DOCUMENT_ROOT . '/core/modules/DolibarrModules.class.php';
{dependances_str}

class {info["class_name"]} extends DolibarrModules
{{
    public function __construct($db)
    {{
        global $langs, $conf;

        $this->db = $db;
        $this->numero = {info["numero"]};
        $this->rights_class = '{module_name}';
        $this->family = "other";
        $this->module_position = '90';
        $this->name = preg_replace('/^mod/i', '', get_class($this));
        $this->description = "{info['description']}";
        $this->version = '1.0.0';
        $this->const_name = 'MAIN_MODULE_' . strtoupper($this->name);
        $this->picto = 'building';
        $this->module_parts = array();
        $this->dirs = array();
        $this->config_page_url = array("{module_name}@immobilier");
        $this->depends = array({depends_str});
        $this->requiredby = array();
        $this->conflictwith = array();
        $this->langfiles = array("{module_name}@immobilier");
        $this->phpmin = array(8, 1);
        $this->need_dolibarr_version = array(23, 0);
        $this->warnings_activation = array();
        $this->warnings_activation_ext = array();

        $this->const = array();
        $this->tabs = array();
        $this->dictionaries = array();

        $this->menu = array();
        $r = 0;
        $this->menu[$r] = array(
            'fk_menu' => 'fk_mainmenu=immobilier',
            'type' => 'top',
            'titre' => '{info["label"]}',
            'mainmenu' => 'immobilier',
            'leftmenu' => '{module_name}',
            'url' => '/custom/{module_name}/index.php',
            'langs' => '{module_name}@immobilier',
            'position' => {info["numero"]},
            'perms' => '1',
            'target' => '',
            'user' => 2,
        );
        $r++;

        $this->rights = array();
        $this->rights_class = '{module_name}';
        $r = 0;
        $this->rights[$r][0] = {info["numero"]}001;
        $this->rights[$r][1] = 'Lire les {info["label"]}';
        $this->rights[$r][3] = 0;
        $this->rights[$r][4] = 'read';
        $r++;
        $this->rights[$r][0] = {info["numero"]}002;
        $this->rights[$r][1] = 'Créer/Modifier les {info["label"]}';
        $this->rights[$r][3] = 0;
        $this->rights[$r][4] = 'write';
        $r++;
        $this->rights[$r][0] = {info["numero"]}003;
        $this->rights[$r][1] = 'Supprimer les {info["label"]}';
        $this->rights[$r][3] = 0;
        $this->rights[$r][4] = 'delete';
    }}

    public function init($options = ''): int
    {{
        $sql = array();
        $result = $this->loadTables();

        if ($result < 0) {{
            return -1;
        }}

        return $this->init($options);
    }}

    public function remove($options = ''): int
    {{
        $sql = array();
        return $this->remove($options);
    }}
}}
"""
    write_file(
        os.path.join(module_dir, "core", "modules", f"{info['class_name']}.class.php"),
        content,
    )


def generate_object_class(module_dir: str, info: dict, module_name: str):
    content = f"""<?php

declare(strict_types=1);

require_once DOL_DOCUMENT_ROOT . '/core/class/commonobject.class.php';

class {info["object_name"]} extends CommonObject
{{
    public $table_element = 'llx_{info["table"]}';
    public $element = '{module_name}';

    public int $rowid;
    public string $ref = '';
    public int $fk_user_creat;
    public string $datec = '';
    public string $tms = '';
    public int $status;

    protected array $fields = array(
        'rowid' => array('type' => 'integer', 'label' => 'ID', 'enabled' => 1, 'visible' => -1, 'notnull' => 1, 'index' => 1, 'position' => 10, 'comment' => 'Id'),
        'ref' => array('type' => 'varchar(128)', 'label' => 'Ref', 'enabled' => 1, 'visible' => 1, 'notnull' => 1, 'showoncombobox' => 1, 'index' => 1, 'position' => 20, 'searchall' => 1, 'comment' => 'Reference'),
        'fk_user_creat' => array('type' => 'integer:User:user/class/user.class.php', 'label' => 'UserAuthor', 'enabled' => 1, 'visible' => -2, 'notnull' => 1, 'position' => 510, 'foreignkey' => 'user.rowid'),
        'datec' => array('type' => 'datetime', 'label' => 'DateCreation', 'enabled' => 1, 'visible' => -2, 'position' => 520),
        'tms' => array('type' => 'timestamp', 'label' => 'DateModification', 'enabled' => 1, 'visible' => -2, 'notnull' => 1, 'position' => 525),
        'status' => array('type' => 'integer', 'label' => 'Status', 'enabled' => 1, 'visible' => 1, 'notnull' => 1, 'default' => 0, 'index' => 1, 'position' => 1000, 'arrayofkeyval' => array(0 => 'Draft', 1 => 'Validated')),
    );

    public function __construct(DoliDB $db)
    {{
        $this->db = $db;
    }}

    public function create(User $user, bool $notrigger = false): int
    {{
        $this->ref = $this->getNextNumRef();
        return $this->createCommon($user, $notrigger);
    }}

    public function fetch(int $id, string $ref = ''): int
    {{
        return $this->fetchCommon($id, $ref);
    }}

    public function update(User $user, bool $notrigger = false): int
    {{
        return $this->updateCommon($user, $notrigger);
    }}

    public function delete(User $user, bool $notrigger = false): int
    {{
        return $this->deleteCommon($user, $notrigger);
    }}

    public function getNextNumRef(): string
    {{
        global $conf;
        $prefix = strtoupper($this->element);
        $date = date('Y');
        $num = $this->getMaxNumRef() + 1;
        return sprintf("%s-%s-%04d", $prefix, $date, $num);
    }}

    protected function getMaxNumRef(): int
    {{
        $sql = "SELECT MAX(CAST(SUBSTRING(ref FROM '-[0-9]+-([0-9]+)$') AS INTEGER)) as maxref";
        $sql .= " FROM ".$this->db->prefix().$this->table_element;
        $resql = $this->db->query($sql);
        if ($resql) {{
            $obj = $this->db->fetch_object($resql);
            return (int) ($obj->maxref ?? 0);
        }}
        return 0;
    }}
}}
"""
    write_file(
        os.path.join(module_dir, "class", f"{info['object_name'].lower()}.class.php"),
        content,
    )


def generate_sql(module_dir: str, info: dict, module_name: str):
    # Main table
    table_sql = f"""-- Table {info['table']}
CREATE TABLE IF NOT EXISTS {{db_prefix}}{info['table']} (
    rowid SERIAL PRIMARY KEY,
    ref VARCHAR(128) NOT NULL,
    fk_user_creat INTEGER NOT NULL,
    datec TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tms TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status INTEGER NOT NULL DEFAULT 0
) TABLESPACE pg_default;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_{info['table']}_ref ON {{db_prefix}}{info['table']}(ref);
CREATE INDEX IF NOT EXISTS idx_{info['table']}_status ON {{db_prefix}}{info['table']}(status);

-- Trigger for tms
CREATE OR REPLACE FUNCTION update_tms_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.tms = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS trg_{info['table']}_tms ON {{db_prefix}}{info['table']};
CREATE TRIGGER trg_{info['table']}_tms
    BEFORE UPDATE ON {{db_prefix}}{info['table']}
    FOR EACH ROW
    EXECUTE FUNCTION update_tms_column();
"""
    write_file(os.path.join(module_dir, "sql", f"llx_{info['table']}.sql"), table_sql)


def generate_lang(module_dir: str, info: dict, module_name: str):
    content = f"""# Dolibarr language file — {module_name}
Module{info['class_name']}Name = {info['label']}
Module{info['class_name']}Desc = {info['description']}
Immobilier = Immobilier
Biens = Biens
Clients = Clients
Location = Location
Vente = Vente
Rénovation = Rénovation
Syndic = Syndic
ÉtudeDeMarché = Étude de marché
Paiements = Paiements
Rapports = Rapports
"""
    write_file(os.path.join(module_dir, "langs", "fr_FR", f"{module_name}.lang"), content)


def generate_test(module_dir: str, info: dict, module_name: str):
    test_content = f"""<?php

declare(strict_types=1);

require_once __DIR__ . '/../../class/{info["object_name"].lower()}.class.php';

class {info["object_name"]}Test extends PHPUnit\\Framework\\TestCase
{{
    protected $object;

    protected function setUp(): void
    {{
        global $db;
        $this->object = new {info["object_name"]}($db);
    }}

    /**
     * @test
     */
    public function tableElementShouldBeCorrect(): void
    {{
        $this->assertEquals('llx_{info["table"]}', $this->object->table_element);
    }}

    /**
     * @test
     */
    public function elementShouldBeCorrect(): void
    {{
        $this->assertEquals('{module_name}', $this->object->element);
    }}

    /**
     * @test
     */
    public function objectShouldHaveRefProperty(): void
    {{
        $this->assertObjectHasProperty('ref', $this->object);
    }}

    /**
     * @test
     */
    public function objectShouldHaveStatusProperty(): void
    {{
        $this->assertObjectHasProperty('status', $this->object);
    }}

    /**
     * @test
     */
    public function getNextNumRefShouldReturnFormattedString(): void
    {{
        $ref = $this->object->getNextNumRef();
        $this->assertStringStartsWith(strtoupper($this->object->element), $ref);
        $this->assertMatchesRegularExpression('/^' . strtoupper($this->object->element) . '-\d{{4}}-\d{{4}}$/', $ref);
    }}
}}
"""
    write_file(
        os.path.join(module_dir, "test", "phpunit", f"{info['object_name']}Test.php"),
        test_content,
    )


def generate_readme(module_dir: str, info: dict, module_name: str):
    content = f"""# {info['label']}

{info['description']} pour Dolibarr ERP.

## Numéro de module
`{info['numero']}`

## Dépendances
{', '.join(info['depends']) if info['depends'] else 'Aucune (module core)'}

## Installation

1. Copier le dossier dans `dolibarr/htdocs/custom/{module_name}/`
2. Activer le module depuis **Configuration > Modules/Applications**
3. Les tables seront créées automatiquement

## Tests

```bash
php test/phpunit/{info['object_name']}Test.php
```

## Structure

```
{module_name}/
├── core/modules/       → Fichier d'activation module
├── class/              → Classes métier
├── sql/                → Schémas de base de données
├── langs/              → Fichiers de traduction
├── test/phpunit/       → Tests automatisés
├── css/                → Feuilles de style
└── js/                 → Scripts JavaScript
```

## License

GPLv3
"""
    write_file(os.path.join(module_dir, "README.md"), content)


def generate_composer(module_dir: str):
    content = """{
    "name": "dolibarr-agence/module",
    "description": "Dolibarr real estate module",
    "type": "project",
    "require-dev": {
        "phpunit/phpunit": "^11.0"
    },
    "autoload": {
        "classmap": [
            "class/"
        ]
    },
    "scripts": {
        "test": "phpunit test/phpunit/"
    }
}
"""
    write_file(os.path.join(module_dir, "composer.json"), content)


def init_git_repo(module_dir: str, module_name: str):
    """Initialize git repo and commit."""
    os.chdir(module_dir)
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "main"], check=False, capture_output=True)
    subprocess.run(["git", "add", "."], check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", f"Initial commit: {module_name} v1.0.0"], check=True, capture_output=True)
    print(f"✓ Git repo initialized for {module_name}")


def create_github_repo(module_name: str):
    """Create GitHub repo via gh CLI."""
    repo_name = f"dolibarr-agence-{module_name}"
    try:
        result = subprocess.run(
            ["gh", "repo", "create", repo_name, "--public", "--source=.", "--push"],
            capture_output=True,
            text=True,
            cwd=os.path.join(BASE_DIR, f"dolibarr-agence-{module_name}"),
        )
        if result.returncode == 0:
            print(f"✓ GitHub repo created and pushed: {repo_name}")
        else:
            print(f"⚠ GitHub create failed for {repo_name}: {result.stderr}")
    except FileNotFoundError:
        print(f"⚠ 'gh' CLI not found. Cannot create GitHub repo for {module_name}.")


def generate_all():
    for module_name, info in MODULES.items():
        print(f"\n===== Generating {module_name} =====")
        module_dir = os.path.join(BASE_DIR, f"dolibarr-agence-{module_name}")

        generate_gitignore(module_dir)
        generate_github_actions(module_dir, module_name)
        generate_module_class(module_dir, info, module_name)
        generate_object_class(module_dir, info, module_name)
        generate_sql(module_dir, info, module_name)
        generate_lang(module_dir, info, module_name)
        generate_test(module_dir, info, module_name)
        generate_readme(module_dir, info, module_name)
        generate_composer(module_dir)

        init_git_repo(module_dir, module_name)
        create_github_repo(module_name)

    print("\n===== All modules generated =====")


if __name__ == "__main__":
    generate_all()
