$('form').on('change', '#id_image', function() {
    var src = URL.createObjectURL(this.files[0]);
    $('#preview-image').attr('src', src);
});

function normalizeSelects(){
    $('#add_category').prop("selectedIndex", 0);
    $('#remove_category').prop("selectedIndex", 0);
};

$('#add_category').on('change', function (e) {
    var optionSelected = $("option:selected", this);
    var valueSelected = this.value;
    var idSelected = optionSelected.data('category-id');

    optionSelected.remove().appendTo($('#remove_category'));
    $('#anime_categories').val($('#anime_categories').val() + " " + valueSelected);
    $('#anime_id_categories').val($('#anime_id_categories').val() + " " + idSelected);

    normalizeSelects();
});


$('#remove_category').on('change', function (e) {
    var optionSelected = $("option:selected", this);

    optionSelected.remove().appendTo($('#add_category'));

    $('#anime_categories').val("")
    $('#anime_id_categories').val("")

    $('#remove_category option:not(:first-child)').each(function() {
        $('#anime_categories').val($('#anime_categories').val() + " " + this.value);
        $('#anime_id_categories').val($('#anime_id_categories').val() + " " + $(this).attr('data-category-id'));
    });

    normalizeSelects();
});
