
function download(path) {
    var element = document.createElement('a');
    element.setAttribute('href', path);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}


function descargar(periodo, nombre, ruta) {
    $.get(ruta+"?periodo="+periodo+"&nombre="+nombre, function(data, status) {
	if(data.enlace == "") {
	    alert("Hubo un error al descargar");
	} else {
	    download(data.enlace);
	}
    });
}

    
