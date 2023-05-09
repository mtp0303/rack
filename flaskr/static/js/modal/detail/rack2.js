

//check box event
$( document ).on("change", ".modal input[type='checkbox']", function(){
    var is_checked = $(this).prop("checked");
    var key = $(this).attr("id");
    var val = "N";
    var data = {};

    if (is_checked) {
        val = "Y"
    }

    data[key] = val;

    $.ajax({
        type: "PUT",
        url: "/modal/detail/" + idx + "/" + rack_detail["row"] + "/" + rack_detail["col"] + "/" + rack_detail["ord"],
        contentType: "application/json",
        data: JSON.stringify(data),
        success: function(result){
            rack = container_data[rack_detail["row"] - 1][rack_detail["row"] - 1][rack_detail["ord"] - 1];
            rack[key] = val;
        }
    })
})

//click event
$( document ).on( "click", "#change", function()
{
    $( this ).parents(".modal-footer").prevAll( ".modal-header" ).find("input").attr( "readonly", false );
    $( this ).parents(".modal-footer").prevAll( ".modal-body" ).find("input").attr( "readonly", false );

    var btn = '<button type="button" class="btn btn-primary" id="modify-save">저장</button>\n\
            <button type="button" class="btn btn-secondary" id="cancel">취소</button>';
    $( this ).replaceWith( btn );
} );

$( document ).on( "click", "#modify-save", function()
{
    var data = {
        "room_idx": idx
    };

    $(".modal input")
        .not("input[type='checkbox']")
        .each(function(i, input){
            var key = $(input).attr("id");
            var val = $(input).val();

            data[key] = val;
        })
    var target = $(this)
    
    $.ajax({
        type: "PUT",
        url: "/modal/detail/" + idx + "/" + rack_detail["row"] + "/" + rack_detail["col"] + "/" + rack_detail["ord"],
        contentType: "application/json",
        data: JSON.stringify(data),
        success: function(result){
            if (result == "success") {
                alert("저장되었습니다");
                return location.reload();
            }

            alert(result);
        }
    })
} );


$( document ).on( "click", "#cancel", function()
{
    for ( var i = 0; i <= Object.keys(rack_detail).length; i++  )
    {
        $ ( "#" + Object.keys( rack_detail )[ i ] ).val( Object.values( rack_detail )[ i ] );
    }

    $( this ).parents(".modal-footer").prevAll( ".modal-header" ).find("input").attr( "readonly", true );
    $( this ).parents(".modal-footer").prevAll( ".modal-body" ).find("input").attr( "readonly", true );

    $( "#cancel" ).parent(".modal-footer").find("#save").remove();
    var btn = '<button type="button" class="btn btn-primary" id="change">변경</button>';
    $( this ).replaceWith( btn );
} );


