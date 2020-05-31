#!/bin/bash

# aqui extraer archivo env cifrado

export DJANGO_SETTINGS_MODULE=servicios_back_end.settings
rq worker default --disable-job-desc-logging
