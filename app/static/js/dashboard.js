$(function() {
	$("em.timeago").each(function(i, e) {
		$(e).html($.timeago($(e).data('datetime')));
	});
});
