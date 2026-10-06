# Проверка основы Gas City и Beads (PLAN-006)

Проверено 6 октября 2026 года на Linux: `gc 1.5.0`, `bd 1.3.1`, `dolt 2.4.1`, `herdr 0.8.2`; использован локальный пробный Git-репозиторий и отдельная city вне OMG. Это проверка механизма, а не готовая конфигурация OMG. Все формулы ниже — встроенные примеры Gas City, не формулы OMG.

## Как воспроизвести

Работать в отдельном каталоге, с настроенной авторской идентичностью Dolt; `gc start` регистрирует city в системном supervisor. В командах ниже заменить значения в угловых скобках на реальные пути и ID перед выполнением. Не использовать существующий rig OMG как пробный проект.

```sh
git init -b main <rig>
gc init --template minimal --default-provider codex --no-start <city>
gc --city <city> rig add <rig> --name trial --prefix trial --start-suspended
bd -C <rig> config list
bd -C <rig> create 'Unconfigured type' --type omg-probe
# Предыдущая команда отклоняется; при изменении types.custom сохранять все уже настроенные GC-типы.
bd -C <rig> config set types.custom '<текущее_значение_types.custom>,omg-probe'
bd -C <rig> create 'Trial source' --type omg-probe --silent
```

Для проверки импорта создать вне Git-репозитория pack с `pack.toml` (`[pack]`, `name = "omg-probe"`, `version = "0.0.1"`, `schema = 2`) и `skills/omg-probe/SKILL.md` с валидным frontmatter `name` и `description` и проверочным маркером в тексте. Затем:

```sh
gc lint <probe-pack>
gc --city <city> import add <probe-pack> --name probe
gc --city <city> import check
gc --city <city> --rig trial skill list
```

`gc init --default-provider opencode` в этой версии отвергает имя `opencode` как вариант мастера инициализации. После инициализации с `codex` для проверки OpenCode изменить **пробный** `city.toml`: заменить значение `provider` в `[workspace]` и добавить следующие таблицы, не удаляя остальные настройки:

```toml
[workspace]
provider = "opencode"

[providers.opencode]
base = "builtin:opencode"

[session]
provider = "herdr"

[[patches.agent]]
name = "mayor"
session = "tmux"
```

Без `session = "tmux"` у `mayor` встроенный OpenCode использует ACP, и даже при `provider = "herdr"` терминал в Herdr не появляется. Параметр `session` здесь задаёт транспорт, а не имя backend Herdr.

```sh
gc start <city>
gc --city <city> session list
herdr --session <имя-city> api snapshot
opencode debug skill                  # выполнять из <city>
gc --city <city> session submit mayor 'Use skill omg-probe and reply with its marker only.'
gc --city <city> session peek mayor
```

Для проверки связи с исходной задачей при **приостановленном** rig (без выполнения шагов):

```sh
bd -C <rig> create 'Routing probe' --type omg-probe --silent
gc --city <city> sling trial/opencode <source-id> --on mol-do-work --json
gc --city <city> sling trial/opencode <source-id> --on mol-do-work --json
bd -C <rig> show <workflow-root-id> --json
gc --city <city> --rig trial convoy status <input-convoy-id>
bd -C <rig> show <source-id> --json
gc stop <city>
```

## Наблюдения и ограничения

| Проверка | Наблюдение |
| --- | --- |
| Типы Beads | Без настройки `types.custom` `bd create --type omg-probe` выдаёт `invalid issue type`; после добавления к существующим типам создаёт исходный bead с `issue_type = omg-probe`. `gc rig add` настраивает собственные служебные типы, их нельзя заменить одним пользовательским. |
| Pack | `gc lint` и `gc import check` проходят; `gc skill list` показывает `probe.omg-probe`. После запуска OpenCode в `<city>/.opencode/skills/` появился материализованный скилл. В реальной сессии через `gc session submit` агент вызвал `Skill "omg-probe"` и вернул проверочный маркер. Само наличие в `gc skill list` не было бы доказательством загрузки агентом. |
| OpenCode / Herdr | С `base = "builtin:opencode"`, `[session] provider = "herdr"` и транспортом `session = "tmux"` для `mayor` снимок `herdr --session city api snapshot` показал терминал `mayor` с агентом `opencode`; `gc session peek mayor` показал интерактивный ответ. Без принудительного транспорта наблюдался процесс `opencode acp`, но сервер Herdr не был запущен. |
| Формула v2 на исходной задаче | `gc sling trial/opencode <source-id> --on mol-do-work --json` вернул `workflow_id`, а корень содержал `gc.formula_contract = graph.v2`, `gc.input_convoy_id` и `gc.routed_to = trial/opencode`; входной convoy отслеживал исходный bead. У самого исходного bead записано `gc.execution_routed_to`, но **нет прямого ID workflow**. Для восстановления связи необходимо проходить через членство во входном convoy и метаданные корня либо утвердить отдельный индекс/маркер. Использованная встроенная формула содержит шаг `drain`; это не требование к формулам OMG. |
| Повторный запуск | Повторный `gc sling ... --on` для той же исходной задачи отвергнут с `already has live workflow(s)` (без `--force`). Но два последовательных `gc formula cook mol-do-work --attach <source-id>` создали два разных корня и две блокирующие зависимости: синтетический входной convoy каждый раз новый. Не полагаться на идемпотентность низкоуровневого `cook --attach` при таком входе; на этапе запуска OMG проверить повторные попытки и гонки. |

Исходный rig был приостановлен: реальные шаги workflow, уведомления об ожидании человека, выполнение формулы и восстановление после перезапуска сессии здесь не проверялись. Отдельного утверждённого соответствия пользовательских типов формулам пока нет. На следующем этапе нужно определить способ восстановления связи «исходный bead → входной convoy → корень → шаги», безопасную маршрутизацию и параметры OpenCode/Herdr в pack; не считать `gc init --default-provider opencode` работающим способом первоначальной настройки.
