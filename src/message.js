export function message(text) {
    var mensagem = document.getElementById("msg");
    mensagem.classList.remove("hideMessage");
    mensagem.classList.add("showMessage");
    mensagem.innerHTML = text;
    setTimeout(
        function(){
            mensagem.classList.remove("showMessage"); 
            mensagem.classList.add("hideMessage"); 
        }, 5500);
  }