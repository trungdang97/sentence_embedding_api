threshold = 0.0

function GetNewsCategory() {
    $.ajax({
        url: "http://localhost:5000/api/v1/newscategory",
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
    params += '&text=' + text

    size = $("#Size").val();
    params += '&size=' + size;

    newscategoryid = $("#Categories").val();
    params += '&newscategoryid=' + newscategoryid;
    setTimeout(() => {
        $.ajax({
            url: "http://localhost:5000/api/v1/news/search/sts" + params,
            dataType: 'json',
            success: function (news) {
                count = 1
                if (news[0]['_score'] < threshold + 1) {
                    $("#Results").append('Không có kết quả phù hợp với yêu cầu tìm kiếm')
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
                            + '<div class="col-sm-1 border-right text-center">' + count + '</div>'
                            + '<div class="col-sm-10">' + element['_source']['title'] + '</div>'
                            + '<div class="col-sm-1 d-flex align-items-center justify-content-center">'
                            + '<button class="btn btn-link similar" title="Tìm kiếm các tiêu đề tương tự" value="'+element['_source']['title']+'"><i class="fas fa-search"></i></button>'
                            + '<button class="btn btn-link" title="Mở rộng nội dung" data-toggle="collapse" data-target="#collps' + count + '" aria-expanded="false" aria-controls="collps' + count + '"><i class="fas fa-chevron-down"></i></button>'
                            + '</div>'
                            + '</div>'
                            + '</div>'
                            + '</div>'
                            + '</div>'
                            + '<div id="collps' + count + '" class="collapse" data-parent="#Results">'
                            + '<div class="card-body">' + body + '</div>'
                            + '</div>'
                        );
                        count += 1;
                    }
                });
                $('.overlay').removeClass('d-flex');
                $("#es_logo").removeClass('d-flex')
            }
        });
    }, 500);
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
