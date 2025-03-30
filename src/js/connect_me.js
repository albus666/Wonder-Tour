function submitForm(event) {
    console.log("ss")
    var form = document.querySelector('.rd-form');
    form.addEventListener('submit', function (event) {
        // event.preventDefault()
        // console.log(event.preventDefault())
        var name = document.getElementById('contact-your-name-2').value;
        var email = document.getElementById('contact-email-2').value;
        var phone = document.getElementById('contact-phone-2').value;
        var message = document.getElementById('contact-message-2').value;
        var url = 'https://www.atopes.xyz/send/33bc92eec5b69fd0487813ff503f91c8';
        var params = 'msg=姓名：' + name + '，邮箱：' + email  + '，留言：' + message;
        // var request = new XMLHttpRequest();
        // request.open('GET', url + '?' + params, true);
        // request.send();
        var request = new XMLHttpRequest();
        request.open('POST', url, true);
        request.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');

        request.send(params);
    });
}
