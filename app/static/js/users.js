$(function() {
	$('.add-user .submit').click(function() {
		if (!$('.add-user').valid()) {
			return;
		}
	});
});
