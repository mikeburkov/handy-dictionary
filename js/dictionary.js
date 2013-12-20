$( document ).ready(function() {
	if ($(location).attr('pathname') == '/') {
		if (!$('#AddWord').hasClass('active')) {
			$('#AddWord').addClass('active')
		}
	} else if ($(location).attr('pathname') == '/viewall'
		|| $(location).attr('pathname') =='/search') {
		if (!$('#ViewAll').hasClass('active')) {
			$('#ViewAll').addClass('active')
		}
		var group = $( ".row" );
		group.each(function () {
			children = $(this).children();
		    equalHeight(children)
		});
	}
});

function equalHeight(group) {
	   tallest = 0;
	   group.each(function() {
	      thisHeight = $(this).height();
	      if(thisHeight > tallest) {
	         tallest = thisHeight;
	      }
	   });
	   group.height(tallest);
}

//$(function() {
//    $('.col-md-3, .col-md-6').each( function( index, item) {
//         var parent = $(item).parent();
//         var $this = $(item);
//         $this.css('line-height', $this.height() + 'px');
//    }); 
//});


