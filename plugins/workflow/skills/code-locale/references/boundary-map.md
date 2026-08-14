# Boundary map — where the line falls, per stack

The rule is in `../SKILL.md`. This file is the lookup table: for each stack, which artifacts are the
machine layer, and what the defect looks like next to the fix.

Every "wrong" column below is a real shape of the reported defect — a Portuguese noun or verb
carried out of an issue and into a name — not an invented strawman.

## Python / FastAPI / SQLAlchemy

| Artifact | Wrong | Right |
|---|---|---|
| Route path | `@app.post("/pedidos")` | `@app.post("/orders")` |
| Query param | `?situacao=aberto` | `?status=open` |
| Response field | `{"quantidade": 3}` | `{"quantity": 3}` |
| Model / DTO | `class PedidoCreate` | `class OrderCreate` |
| Function | `def buscar_pedido(id)` | `def get_order(order_id)` |
| Table / column | `pedidos.data_entrega` | `orders.delivered_at` |
| Enum value | `Status.PENDENTE` | `Status.PENDING` |
| Error code | `PEDIDO_NAO_ENCONTRADO` | `ORDER_NOT_FOUND` |
| Env var | `PEDIDO_TIMEOUT` | `ORDER_TIMEOUT` |
| Log field key | `logger.info(..., pedido_id=x)` | `logger.info(..., order_id=x)` |

The human sentence inside that log call stays in the repo's language:
`logger.info("pedido criado com sucesso", order_id=x)` is correct on both halves.

Format-level conventions for this stack — the `XCreate` / `XUpdate` / `XData` DTO triple, the
`UPPER_SNAKE_CASE` response-code registry, domain-prefixed env vars, `test_*_adversarial` naming —
belong to `python-rest-api` and are unaffected by this skill. That skill governs *shape*; this one
governs *language*.

## Lua / FiveM

String-typed contracts are the exposure here: nothing in Lua fails at build time when a name drifts,
so an event name in the wrong language is a permanent name.

| Artifact | Wrong | Right |
|---|---|---|
| Event name | `RegisterNetEvent("loja:comprar")` | `RegisterNetEvent("shop:purchase")` |
| Export | `exports("darItem", fn)` | `exports("giveItem", fn)` |
| StateBag key | `Player(src).state.dinheiro` | `Player(src).state.cash` |
| NUI action | `SendNUIMessage({acao = "abrir"})` | `SendNUIMessage({action = "open"})` |
| File / module | `actions/loja/loja_def.lua` | `actions/shop/shop_def.lua` |
| Resource-local fn | `local function calcularPreco()` | `local function calculatePrice()` |

Chat output, notification text and any string the player reads stay in the game's language.

## C# / .NET (AssettoServer plugin)

| Artifact | Wrong | Right |
|---|---|---|
| Class / method | `class GerenciadorDeCorrida` | `class RaceManager` |
| Plugin config key | `tempoMaximo: 300` | `maxDurationSeconds: 300` |
| Config file | `cfg/plugin_corrida_cfg.yml` | `cfg/plugin_race_cfg.yml` |
| Chat command | `[Command("corrida")]` | `[Command("race")]` |
| Test method | `Deve_iniciar_corrida()` | `Starts_race_when_grid_is_full()` |

## React / TypeScript

| Artifact | Wrong | Right |
|---|---|---|
| Component | `function ListaDePedidos()` | `function OrderList()` |
| Prop | `<Card titulo={x} />` | `<Card title={x} />` |
| Hook | `useCarrinho()` | `useCart()` |
| Store slice / action | `pedidoSlice`, `adicionarItem` | `orderSlice`, `addItem` |
| CSS class / token | `.botao-primario` | `.button-primary` |
| Route | `/meus-pedidos` | `/my-orders` |

Every visible label — button text, headings, validation messages — stays in the product's language.
The rule bites the prop name, never the prop value.

## SQL / migrations

| Artifact | Wrong | Right |
|---|---|---|
| Table | `CREATE TABLE clientes` | `CREATE TABLE customers` |
| Column | `data_nascimento` | `birth_date` |
| Index | `idx_pedidos_situacao` | `idx_orders_status` |
| Constraint | `chk_saldo_positivo` | `chk_positive_balance` |
| Migration slug | `20260814_criar_pedidos` | `20260814_create_orders` |
| Persisted enum value | `'PENDENTE'` | `'PENDING'` |

A persisted enum value is a contract with every stored row: it is machine layer, and changing it
later is a data migration, not a rename. Display labels for those values live in the presentation
layer, in the product's language.

## Helm / Kubernetes / config

| Artifact | Wrong | Right |
|---|---|---|
| values.yaml key | `replicasProducao: 3` | `productionReplicas: 3` |
| Secret / ConfigMap key | `senha-banco` | `database-password` |
| Consul/KV path | `config/loja/desconto` | `config/shop/discount` |
| CLI flag | `--saida-json` | `--json-output` |
| Metric name | `pedidos_criados_total` | `orders_created_total` |
| Metric label key | `{situacao="aberto"}` | `{status="open"}` |

A metric **label value** may legitimately be a domain term; the label **key** may not.

## The one exception, everywhere

Brazilian legal and regulatory instruments keep their names, deaccented, inside English grammar:
`cpf`, `cnpj`, `cep`, `boleto`, `pix`, `nota_fiscal`, `sefaz`, `renavam`, `crlv`, `cnh`, `fgts`,
`inss`, `icms`. They are legitimate only through the item's Glossary or an inline
`locale-ok: <reason>` — see `../SKILL.md`.

`nota_fiscal_number` is right. `nota_fiscal_numero` is not: the noun is kept, the grammar around it
is English.
