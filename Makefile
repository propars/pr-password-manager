


ifneq "$(NO_CACHE)" "true"
	NO_CACHE := "false"
endif



build:
	docker build --no-cache=$(NO_CACHE) -t pr_password_manager .



run:
	docker run -tid --name prpassman \
        --expose 8000 \
        -v ${CURDIR}/prpassman:/home/propars/prpassman \
        -v ${CURDIR}/DATA:/home/propars/DATA \
        -v /etc/localtime:/etc/localtime:ro \
        -e DJANGO_SETTINGS_MODULE="prpassman.production_settings" \
        pr_password_manager
