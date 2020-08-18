#!/usr/bin/env bash

function procesar_ee() {
    local ee="$1"
    local ee_path="$2"
    cd "$ee_path"
    zip -r "$ee.zip" "actividades" "evaluaciones"
    rm -R "actividades"
    rm -R "evaluaciones"
    cd -
}

function procesar_periodo() {
    local ruta_periodo="$1"
    for ee in $(ls "$ruta_periodo"); do
	procesar_ee "$ee" "$ruta_periodo/$ee"
    done
}


function main() {
    local base_path="$1"
    separador=$IFS
    IFS=""
    IFS=$(echo -en "\n\b")
    echo "entra"
    for periodo in $(ls "$base_path"); do	
	procesar_periodo "$base_path/$periodo"
    done
    IFS=$separador
}

main $1
