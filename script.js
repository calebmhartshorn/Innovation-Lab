document.getElementById("postBtn").addEventListener( "click", ()=>{postRequest("http:/192.168.1.23:8080/hello")})
document.getElementById("getBtn").addEventListener(  "click", ()=>{getRequest("http:/192.168.1.23:8080/hello")})
document.getElementById("clearBtn").addEventListener("click", ()=>{getRequest("http:/192.168.1.23:8080/clear")})

function getRequest(url) {
  request = new Request(url);

  fetch(request)
    .then((response) => response.text())
    .then((html) => {
      console.log(html);
      
      let elements = Array.from(document.getElementsByClassName('result'))
      elements.forEach(e => {
        console.log(e)
        e.remove()
      })

      let p = document.createElement('p')
      p.innerText = html
      p.classList.add("result")
      document.getElementById('body').appendChild(p)
    })
    .catch((error) => {
      console.error('Error:', error);
    });
}

function postRequest(url) {

  request = new Request(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message: document.getElementById("message").value
    })
  });

  fetch(request)
 .then((response) => response.text())
 .then((html) => {
   console.log(html);
 })
 .then(() => {
  getRequest("http:/192.168.1.23:8080/hello")
 })
 .catch((error) => {
   console.error('Error:', error);
 });
}
