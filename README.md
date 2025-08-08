## Exploitation guide

[Windows only] *0) After cloning you need to change CRLF to LF for file ./entrpoint.sh, or backend would fail to start.

1) Run service with database:
```bash
docker compose -f compose.yaml up -d
```
2) Go to `0.0.0.0:8000/docs`. Here comes the API documentation.

3) On right page side click `Authorize`.

4) Use `APP_API_KEY` from `.env` to authorize in API.

5) In each section of request click `Try it out` and test routes.

## Data view from Postgres

### Table `activities`
| tag            | bitmap   |
|----------------|----------|
| Milk           | 00000001 |
| Butter         | 00000010 |
| Dairy Products | 00000011 |
| Pork           | 00000100 |
| Beef           | 00001000 |
| Meat Products  | 00001100 |
| Food           | 00001111 |
| Cargo          | 00010000 |
| Passenger      | 00100000 |
| Parts          | 01000000 |
| Accessories    | 10000000 |
| Vehicle        | 11110000 |

### Table `buildings`
| id | address                 | geo_point                                     |
|----|-------------------------|-----------------------------------------------|
|  1 | Блюхера, 32/1           | POINT (0 0)                                   |
|  2 | Блюхера, 32/2           | POINT (0 0.000009009009009)                   |
|  3 | Коммунистическая, 1091  | POINT (0.009009009009009 0)                   |
|  4 | Покрышкина, 14          | POINT (0 0.0045045045045045)                  |
|  5 | Пивоваров, 911          | POINT (0.0030027027027027 0.0030027027027027) |
|  6 | Постакадемическая, 16к4 | POINT (0.009009009009009 0.009009009009009)   |
|  7 | Балабановская, 16       | POINT (0 0)                                   |
|  8 | Дробышевская, 91/4      | POINT (0.000009009009009 0)                   |
|  9 | Лейбница, 56            | POINT (0 0.009009009009009)                   |
| 10 | Карамзина, 77           | POINT (0.0045045045045045 0)                  |
| 11 | Столяров, 80к1          | POINT (0.0060054054054054 0.0060054054054054) |
| 12 | Академическая, 16к4     | POINT (0.0135135135135135 0)                  |

### Table `organizations`
| id | name                         | phone_numbers                     | building_id | activity_tag   |
|----|------------------------------|-----------------------------------|-------------|----------------|
|  1 | ООО "Моя Оборона"            | {+7(911)111-11-11,11-111-11}      |          12 | Milk           |
|  2 | ЗАО "Блачные цены"           | {"+385 7777-77-77"}               |          11 | Butter         |
|  3 | ОАО "Везение"                | {"+91 222-11-22"}                 |          10 | Dairy Products |
|  4 | ООО "Лучшая компания"        | {2-222-222,88002222222}           |           9 | Pork           |
|  5 | ЗАО "Худший предприниматель" | {333-33-33}                       |           8 | Beef           |
|  6 | ОАО "Разадача"               | {8-800-555-35-35}                 |           7 | Meat Products  |
|  7 | ООО "Стаканы на столах"      | {112}                             |           6 | Food           |
|  8 | ЗАО "Чёрное солнце"          | {1-345-123-45-61}                 |           5 | Cargo          |
|  9 | ОАО "Ели мясо мужики"        | {"+64 1234567"}                   |           4 | Passenger      |
| 10 | ООО "Куда уходит детство"    | {11-175-479-23-76}                |           3 | Parts          |
| 11 | ЗАО "Мир"                    | {+79547341925}                    |           2 | Accessories    |
| 12 | ОАО "Губанов"                | {4-444-444,444-44-44,88004444444} |           1 | Vehicle        |
