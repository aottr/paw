alias cw := css-watch
alias cb := css-build

css-setup:
    cd theme && npm ci
css-watch:
    npx tailwindcss@3.4.1 -c ./theme/tailwind.config.js --content ./**/*.html -i ./theme/input.css -o ./paw/static/css/paw.css -w
css-build:
    npx tailwindcss@3.4.1 -c ./theme/tailwind.config.js -i ./theme/input.css -o ./paw/static/css/paw.css -m

create admin:
    poetry run python manage.py createsuperuser
