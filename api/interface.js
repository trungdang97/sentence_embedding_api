host = "http://192.168.1.100:5000"
threshold = 0.6

function GetNewsCategory() {
    $.ajax({
        url: host+"/api/v1/newscategory",
        dataType: 'json',
        success: function (tuples) {
            tuples.forEach(element => {
                $('#Categories').append(new Option(element['name'], element['id']));
            });
        }
    });
}

function STS_Search() {
    $("#Results").empty();
    $("#es_logo").addClass('d-flex')
    $('.overlay').addClass('d-flex');

    params = "?";

    text = $("#Query").val();
    if(text == ''){
        $("#Results").append('Ô tìm kiếm không có dữ liệu.')
        $('.overlay').removeClass('d-flex');
        $("#es_logo").removeClass('d-flex');
        return;
    }
    params += '&text=' + text

    size = $("#Size").val();
    params += '&size=' + size;

    isTitle = $("#IsTitle").val();
    params += '&isTitle=' + isTitle;

    newscategoryid = $("#Categories").val();
    params += '&newscategoryid=' + newscategoryid;
    setTimeout(() => {
        $.ajax({
            url: host+"/api/v1/news/search/sts" + params,
            dataType: 'json',
            success: function (news) {
                if(news == null || news.length == 0){
                    $("#Results").append('Không có kết quả phù hợp với yêu cầu tìm kiếm')
                    $('.overlay').removeClass('d-flex');
                    $("#es_logo").removeClass('d-flex');
                    return;
                }
                count = 1;
                if (news[0]['_score'] < threshold + 1) {
                    $("#Results").append('Không có kết quả phù hợp với yêu cầu tìm kiếm')
                }
                if(news.length > size){
                    news.splice(size,news.length-size)
                }
                news.forEach(element => {
                    if (element['_score'] >= threshold + 1) {
                        body = '<b>Không có dữ liệu!</b>'
                        if (element['_source']['body'] != '' && element['_source']['body'] != null) {
                            body = element['_source']['body']
                        }
                        $("#Results").append(
                            '<div class="card">'
                            + '<div class="card-header" id="head' + count + '">'
                            + '<div class="mb-0">'
                            + '<div class="row">'
                            + '<div class="col-sm-1 border-right text-center news-index">' + count + "<br/><span class='cs_sim font-weight-bold' style='display:None'>("+(element['_score']-1).toFixed(2)+")</span>" + '</div>'
                            + '<div class="col-sm-10">' + "<span id='Title"+count+"' class='news-index'>" + element['_source']['title'] + "</span><hr/>" + "<p id='Abstract"+count+"' class='abstract'>" + element['_source']['abstract'] + "</p>" + '</div>'
                            + '<div class="col-sm-1 d-flex align-items-center justify-content-center">'
                            + '<button id="SimilarSearch'+ count +'" class="btn btn-link similar" title="Tìm kiếm tương tự" value="'+element['_source']['title']+'"><i class="fas fa-search"></i></button>'
                            + '<button class="btn btn-link" title="Mở rộng nội dung" data-toggle="collapse" data-target="#collps' + count + '" aria-expanded="false" aria-controls="collps' + count + '"><i class="fas fa-chevron-down"></i></button>'
                            + '<button class="btn btn-danger delete" value="'+element['_id']+'" onclick="Delete(this)" style="display:None" title="Xóa bản ghi"><i class="fas fa-trash-alt"></i></button>'
                            + '</div>'
                            + '</div>'
                            + '</div>'
                            + '</div>'
                            + '</div>'
                            + '<div id="collps' + count + '" class="collapse" data-parent="#Results">'
                            + '<div class="card-body">' + "<p><b>" + element['_source']['abstract']+ "</b></p><br/>" + body + '</div>'
                            + '</div>'
                        );
                        if(element['_isTitle']==false || isTitle=='0'){
                            $("#SimilarSearch"+count).val(element['_source']['abstract'])
                        }
                        if(element['_isTitle']==true){
                            $("#Title"+count).addClass("font-weight-bold")
                        }
                        else if(element['_isTitle']==false){
                            $("#Abstract"+count).addClass("font-weight-bold")
                        }
                        else if(isTitle=='1'){
                            $("#Title"+count).addClass("font-weight-bold")
                        }
                        else if(isTitle=='0'){
                            $("#Abstract"+count).addClass("font-weight-bold")
                        }
                        count += 1;
                    }
                });
                DevMode()
                $('.overlay').removeClass('d-flex');
                $("#es_logo").removeClass('d-flex');
            }
        });
    }, 500);
}

DEV=false
function DevModeToggle(){
    DEV = !DEV
    DevMode()
}

function DevMode(){
    if(DEV){
        $("#devmode").removeClass('btn-primary')
        $("#devmode").addClass('btn-danger')
        $(".cs_sim").show()
        $(".delete").show()
    }
    else{
        $("#devmode").removeClass('btn-danger')
        $("#devmode").addClass('btn-primary')
        $(".cs_sim").hide()
        $(".delete").hide()
    }
}

toastr.options = {
    "closeButton": true,
    "debug": false,
    "newestOnTop": false,
    "progressBar": true,
    "positionClass": "toast-bottom-right",
    "preventDuplicates": false,
    "onclick": null,
    "showDuration": "300",
    "hideDuration": "1000",
    "timeOut": "5000",
    "extendedTimeOut": "1000",
    "showEasing": "swing",
    "hideEasing": "linear",
    "showMethod": "fadeIn",
    "hideMethod": "fadeOut"
}
function Delete(e){
    id = e.value
    params = "?id="+id
    $.ajax({
        url: host+"/api/v1/news/delete" + params,
        dataType: 'json',
        method: 'delete',
        success:function(response){
            if(response['result']=='deleted'){
                toastr["success"]("Xóa bản ghi thành công", "Thành công")
                STS_Search()
            }
        }
    });
}

$(document).ready(function () {
    GetNewsCategory();
    $('#Query').keypress(function (e) {
        if (e.keyCode == '13') {
            STS_Search()
        }
    });
    $('#Results').on('click', '.similar', function(){
        $('#Query').val(this.value)
        STS_Search()
    })
});
