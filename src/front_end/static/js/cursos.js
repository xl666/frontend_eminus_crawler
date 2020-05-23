$(function(){

    var seleccionados = [];
    
    $("#formulario").submit(function(e) {
	seleccionados = [];
	cursos = $("#tabla_cursos").children();
	for(c = 0; c < cursos.length; c++) {
	    elementos = cursos[c].children;
	    if (elementos[1].children[0].children[0].children[0].checked) {
		seleccionados.push(elementos[0].innerHTML);
	    }
	}
	var ids = seleccionados.toString();
	if (ids == "") {
	    var original = $("#botonExtraccion").text();
	    $("#botonExtraccion").text("Selecciona al menos uno");
	    setTimeout(function() {
		$("#botonExtraccion").text(original);
	    }, 3000);
	    return false;
	}
	$("#ids").val(ids);
    });
});
