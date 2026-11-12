# Реестр тестеров — шаблон

Файл содержит только обезличенные записи. Персональные данные тестеров храним у владельца в закрытом месте, не в Git.

| tester_id | сегмент | устройство/OS | APK build | выдано | сценарий | результат | bug | повторит тест | отзыв разрешён | заметки |
|---|---|---|---|---|---|---|---|---|---|---|
| T-001 | salsa/beginner | Android model / OS | 0.1.0-beta+12 | YYYY-MM-DD | first run; choreography; training | pending | — | yes/no | yes/no | — |
| T-002 | bachata/intermediate | Android model / OS | 0.1.0-beta+12 | YYYY-MM-DD | first run; choreography; training | pending | — | yes/no | yes/no | — |
| T-003 | caucasus | Android model / OS | 0.1.0-beta+12 | YYYY-MM-DD | first run; choreography; training | pending | — | yes/no | yes/no | — |
| T-004 | other | Android model / OS | 0.1.0-beta+12 | YYYY-MM-DD | first run; choreography; training | pending | — | yes/no | yes/no | — |
| T-005 | other | Android model / OS | 0.1.0-beta+12 | YYYY-MM-DD | first run; choreography; training | pending | — | yes/no | yes/no | — |

## После каждой сессии

- Установилось ли APK?
- Что пользователь сделал без объяснений?
- Где остановился или запутался?
- Создал ли/открыл ли хореографию?
- Завершил ли тренировку?
- Что захотел повторить?
- Какая Pro-функция кажется ценной?
- Разрешён ли обезличенный отзыв для сайта/маркетинга?

Статусы: pending / pass / issue / blocked. Ошибка должна ссылаться на отдельный тикет и содержать шаги воспроизведения, устройство, OS и APK build.
