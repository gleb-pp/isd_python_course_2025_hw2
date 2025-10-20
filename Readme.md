##### Линтеры

`make format`

`make lint`

##### Как работать с Poetry

1) Создаете отдельную среду для poetry, отдельную для проекта: .venv и .venv_poetry
2) Устанавливаете poetry через pip в .venv_poetry ` source .venv_poetry/bin/activate; pip install poetry`
3) В .venv проекта устанавливаете нужные зависимости через poetry из venv_poetry
   1) `source .venv/bin/activate; .venv_poetry/bin/poetry install --no-root`

Таким образом не смешиваются завимистои poetry и вашего проекта. Обычно, лучше сделать общий poetry для каждой версии python и во всех проектах системы использовать его.
####  Здесь должно быть описание, что было сгенерированно LLM
