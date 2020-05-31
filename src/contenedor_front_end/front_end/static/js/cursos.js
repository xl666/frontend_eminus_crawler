$(function(){

    function es_terminado() {
	var url = window.location.href;
	var pos = url.indexOf("?terminados=true");
	if(pos == -1) {
	    return false;
	}
	return true;
    }

    
    var seleccionados = [];
    var periodos = [];
    var nombres = []
    
    $("#formulario").submit(function(e) {
	seleccionados = [];
	periodos = [];
	nombres =[];
	cursos = $("#tabla_cursos").children();
	for(c = 0; c < cursos.length; c++) {
	    elementos = cursos[c].children;
	    if (elementos[1].children[0].children[0].children[0].checked) {
		seleccionados.push(elementos[0].innerHTML);
		periodos.push(elementos[2].innerHTML);
		nombres.push(elementos[3].innerHTML);
	    }
	}
	var ids = seleccionados.toString();
	var ps = periodos.toString();
	var ns = nombres.toString();
	if (ids == "") {
	    var original = $("#botonExtraccion").text();
	    $("#botonExtraccion").text("Selecciona al menos uno");
	    setTimeout(function() {
		$("#botonExtraccion").text(original);
	    }, 3000);
	    return false;
	}
	$("#ids").val(ids);
	$("#periodos").val(ps);
	$("#nombres").val(ns);
	if(es_terminado()) {
	    $("#terminados").val("true");
	}
    });
});
