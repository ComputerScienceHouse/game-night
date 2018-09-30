$(document).ready(function() {
    $(document).on("click", "select", function(event) {
        event.stopPropagation();
    });
});