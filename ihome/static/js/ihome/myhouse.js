$(document).ready(function(){
    //只有认证之后的用户才可以发布房源，先判断用户的实名认证状态
    $.get("/api/v1.0/users/auth", function (resp) {
        if ("4101" == resp.errno) {
            //用户未登陆
            location.href = "/login.html"
        } else if ("0" == resp.errno) {
            //没有认证的用户，在页面显示去认证
            if (!(resp.data.real_name && resp.data.id_card)) {
                    $(".auth-warn").show();
                    return
            }
            //已经认证的用户，请求其之前发布的房源信息
            $.get("/api/v1.0/user/houses", function (resp) {
                if (resp.errno == "0") {
                    $("#houses-list").html(template("houses-list-tmpl", {houses:resp.data.houses}))
                } else {
                    $("#houses-list").html(template("houses-list-tmpl", {houses: []}));
                }
            });
        }
    })
});