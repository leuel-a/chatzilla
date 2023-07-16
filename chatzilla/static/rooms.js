#!/usr/bin/node
let currentRoom  = null;
const socket = io({autoConnect: false});

window.addEventListener('load', () => {
  if (currentRoom === null) {
    const messageSpace = document.getElementById('message-space');
    const showMessage = document.createTextNode('Please choose a room to start chatting!');
    messageSpace.classList.add('d-flex', 'align-items-center', 'justify-content-center', 'text-muted');
    messageSpace.appendChild(showMessage);
  }
})

function setCurrentRoom(roomName, clickedElement)  {
  currentRoom = roomName;
  socket.connect();

  const roomList = document.getElementById('room-list');
  const roomItems = document.getElementsByTagName('li');
  for (let i = 0; i < roomItems.length; i++) {
    roomItems[i].querySelector('.ms-2').classList.remove('selected-room')
  }
  clickedElement.querySelector('.ms-2').classList.add('selected-room');
  const messageSpace = document.getElementById('message-space');
  messageSpace.innerHTML = '';
  messageSpace.classList.remove('d-flex', 'align-items-center', 'justify-content-center', 'text-muted');
  messageSpace.classList.add('container', 'd-flex', 'flex-column', 'align-items-start', 'pl-5', 'pt-4');
  const listGroup = document.createElement('ol');
  listGroup.classList.add('list-group', 'list-group-numbered');
  listGroup.setAttribute('id', 'message-list');
  messageSpace.appendChild(listGroup);
}

function addTextMessage(message, user) {
  const messageSpace = document.getElementById('message-space');
  const sendMessage = document.createTextNode(user + ': ' + message);
  const lineBreak = document.createElement('br'); // Create a <br> element
  messageSpace.appendChild(sendMessage);
  messageSpace.appendChild(lineBreak); // Append the line break element
}


document.getElementById('form-message').addEventListener('submit', function (event) {
  event.preventDefault();
  if (currentRoom === null) {
    window.alert('Please choose a room to start chatting!');
    return;
  }

  const message = document.getElementById('message-input').value.trim();
  if (message === '') {
    return;
  }

  socket.emit('new-message', message, currentRoom);
  document.getElementById('message-input').value = '';
});


socket.on('chat', function (data) {
  addTextMessage(data.message, data.user);
});

let data = null;
let isRoomChecked = false;

$('#createRoomForm').on ('submit',  function (e) {
 // if ajax set this to true, it will not go here when it triggers.
 if (!isRoomChecked) {
   e.preventDefault(); // put preventDefault here not inside the ajax success function
   const roomName = $('#room_name').val();
   $.ajax( {
     type: "POST",
      url: "/validate_room/" + roomName,
      cache: false,
      success: function (result) {
         // if result is set to true
         isRoomChecked = true;
         data = result.value;
         // then trigger to submit of the form
         $('#createRoomForm').trigger('submit');
      }
    });
 } else {
   // form is submitted
   if (data === true) {
     e.preventDefault();
     const parent = document.getElementById('roomLabelGroup');
     const errorDiv = document.createElement('div');
     const errorText = document.createTextNode('That room name is taken. Please choose a different one.');

     errorDiv.classList.add('invalid-feedback');
     errorDiv.style.display = 'block';
     errorDiv.textContent = '';
     errorDiv.appendChild(errorText);
     parent.appendChild(errorDiv);
   }
   isRoomChecked = false;
   data = null;
   console.log('form submitted');
 }
});


document.getElementById('room-list').addEventListener('click', function (event) {
  // Get the element that was clicked and also the content of the element
  const clickedElement = event.target.closest('li');
  const roomName = clickedElement.querySelector('.ms-2').textContent;
  console.log(roomName);
  setCurrentRoom(roomName, clickedElement);

  socket.disconnect(false);
  // Send an AJAX request to the backend to get all the messages in the currentRoom
  $.ajax({
    type: 'GET',
    url: '/api/messages/' + roomName,
    cache: false,
    success: function (result) {
      const room_messages = result.messages;
      for (let i = 0; i < room_messages.length; i++) {
        addTextMessage(room_messages[i].message, room_messages[i].username);
      }
    }
  });

  socket.connect();
});

autosize(document.querySelectorAll('textarea'));


