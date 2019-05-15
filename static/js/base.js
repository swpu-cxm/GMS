//导航栏动态效果切换
// var ul = document.querySelector(".navbar-nav");
// var N = ul.firstElementChild;
// ul.addEventListener("click", clickHandler);
//
// function clickHandler(e) {
//     if (e.target instanceof HTMLUListElement) return;
//     if (e.target instanceof HTMLLIElement) return;
//     if (N) {
//         N.className = "";
//     }
//     N = e.target.parentElement;
//     N.className = "active";
// }

$('.navbar-nav li').click(function (event) {
    //$('.navbar-nav li').removeClass('active');
    console.log('ok');
    alert(event.target.text());
    console.log('ok');
    event.target.addClass('active');
})

$(function () {
    $(".navbar-nav").find("li").each(function () {
        var a = $(this).find("a:first")[0];
        if ($(a).attr("href") === location.pathname) {
            $(this).addClass("active");
        } else {
            $(this).removeClass("active");
        }
    });
})