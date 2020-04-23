$(document).ready(function () {
    var mediaSource
    var duration
    var title
    var timeA

    $('#capacity').prop("disabled", true)

    var sourceopen = function (e) {
        URL.revokeObjectURL($('video[name=media]').attr('src'))
        let mimeType = sessionStorage.getItem("mimeType")
        var mediaSource2 = this
        mediaSource2.duration = duration
        let sourceBuffer = mediaSource2.addSourceBuffer(mimeType)

        let videoURL = 'load/'

        load()

        timeA = setInterval(function A() {
            if ($('video[name=media]').prop("buffered").length > 0) {
                var b = sourceBuffer.buffered

                if ($('video[name=media]').prop("buffered").end(0) < duration) {

                    if ($('video[name=media]').prop("buffered").length > 0 && Math.round($('video[name=media]').prop("buffered").end(0)) >= $('video[name=media]').prop("currentTime") + 20){

                        if ($('video[name=media]').prop("currentTime") >= $('video[name=media]').prop("buffered").end(0) - 5){
                            load()
                        }

                    } else if ($('video[name=media]').prop("buffered").length > 0 && $('video[name=media]').prop("buffered").end(0) < $('video[name=media]').prop("currentTime") + 20) {
                        load()
                    }

                } else if ($('video[name=media]').prop("buffered").end(0) >= duration) {
                    clearInterval(timeA)
                }
            }
        }, 1000)

        function load(){
            fetch (videoURL)
            .then (function (response) {
                return response.arrayBuffer()
            })
            .then(function (arrayBuffer){
                if (arrayBuffer.byteLength > 0) {
                    sourceBuffer.appendBuffer(arrayBuffer)
                }
            })
        }
    }

    function ajaxRequestMain(title) {
        $.ajax({
            url: "creating_a_loader/",
            type: "post",
            dataType: "json",
            data: {"csrfmiddlewaretoken": $("input[type=hidden]").val(),
            "capacity" : $("#capacity").val(), 'currentTime': $('video[name=media]').prop("currentTime")},
            success: function(data) {

                $("#title").text(title)
                $("#title").css({
                    "visibility": "visible",
                    "margin-top": "5px",
                    "margin-bottom": "5px",
                });

                $("#video").css({
                    "visibility": "visible",
                    "margin-top": "0px",
                    "margin-bottom": "0px",
                    "width": "75%",
                    "height": "45%"
                });

                $('.block3').css({
                    'visibility': 'visible',
                })

                if (!mediaSource) {
                    mediaSource = new MediaSource()
                    mediaSource.addEventListener("sourceopen", sourceopen)
                    duration = data['duration']
                    sessionStorage.setItem("mimeType", `${data['mimeType']}; codecs="${data['acodec']}, ${data['vcodec']}"`)
                    $('video[name=media]').attr('src', window.URL.createObjectURL(mediaSource))
                }
            },
            error: function(){
                alert("Ошибка выполнения Ajax запроса по созданию Thread")
            }
        })
    }

    // определение доступных качеств видео... добавление в тег select
    function ajaxRequestToLoadCapacitys() {
        $.ajax({
            url: "load_capacity/",
            type: "post",
            dataType: "json",
            data: {"csrfmiddlewaretoken": $("input[type=hidden]").val(),
            "ref": $("#refToVideo").val()},
            success: function(data) {
                if (data){

                    let array = data['string'].split("/")
                    $("#capacity").append($('<option value="0">--Выберите качество--</option>'))
                    for (let i = 0; i < array.length - 1; i++) {
                        $("#capacity").append($('<option value='+ array[i] +'>'+ array[i] +'</option>'))
                    }

                    array = data['stringNormalVideo'].split("/")
                    $("#selectDownload").append($('<option value="0">--Выберите качество--</option>'))
                    for (let i = 0; i < array.length - 1; i++) {
                        $("#selectDownload").append($('<option value='+ array[i] +'>'+ array[i] +'</option>'))
                    }

                    $('#capacity').prop("disabled", false)
                    $('#capacity option:first').prop("selected", true)

                    $(".block2").append($('<video id="video" style="visibility: hidden; margin-top: 0px; margin-bottom: 0px;" name="media" controls></video>'))
                    title = data['title']

                } else if (!data) {
                    alert("Ошибка \n\n\n По некоторой причине возникла ошибка \n Возможно у вас не работает интернет \т Возможно вы указали неправильно ссылку")
                    clearInterval(timeA)
                    $("#title").text("")
                    mediaSource.removeEventListener('sourceopen', sourceopen)
                    mediaSource = NaN
                    $("video[name=media]").detach()
                    //очищаю всплывающий список
                    $("#capacity").empty()
                }
            },
            error: function(){
            }
        })
    }

    $("#capacity").on('change', function(e) {
        if($(this).val() == "0") {
            return false
        } else {
            ajaxRequestMain(title)
        }
    })

    $("#selectDownload").on('change', function(e) {
        if ($(this).val() == "0") {
            return false
        } else {
            $.ajax({
                url: "download/",
                type: "post",
                dataType: "text",
                data: {"csrfmiddlewaretoken": $("input[type=hidden]").val(),
                    'resolution': $(this).val()},
                success: function(data) {

                    if (data != ""){

                        $('.sf-quick-dl-btn').attr('href', `${data}`)
                        $('.sf-quick-dl-btn').attr('download', `${title}.mp4`)
                        let a = document.querySelector('a[class=sf-quick-dl-btn]')
                        a.click()

                    } else {

                        alert("По какой-то причине невозможно скачать видео 2")

                    }

                },
                error: function(){

                    alert("По какой-то причине невозможно скачать видео")

                }
            })
        }
    })

    $("#refToVideo").on('input',function (e) {
        if ($("#refToVideo").val())
            ajaxRequestToLoadCapacitys()
    })
});