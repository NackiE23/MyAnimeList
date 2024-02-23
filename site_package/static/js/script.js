$(document).ready(function() {
    $(".message_close").on('click', function() {
        $(this).parent().fadeOut("fast");
    });
});
