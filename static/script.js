document.addEventListener("DOMContentLoaded", function() {
  var showFormLinks = document.getElementsByClassName("show-form");  
  var linkForm = document.getElementById("form-container");
  var showSearch= document.getElementById("show-search");
  var searchForm = document.getElementById("search-container")

  Array.from(showFormLinks).forEach(function(link) {
    link.addEventListener("click", function(event) {
      event.preventDefault();
      linkForm.classList.toggle("hidden");
      if(!linkForm.classList.contains("hidden")){
        console.log("linkForm is showing need to hide search")
      }
      focusFirstInput(linkForm);
    });
  });

  focusFirstInput(document.getElementById("form-container"));

  if(showSearch!==null){
    showSearch.addEventListener("click", function(event) {
      event.preventDefault();
      searchForm.classList.toggle("hidden");
      if (!searchForm.classList.contains('hidden')){
        focusFirstInput(searchForm)
      }
    });
  }

  const scrollToTopButtons = document.querySelectorAll('.toTop');
  scrollToTopButtons.forEach(button => {
    button.addEventListener('click', () => {      
        window.scrollTo({
          top: 0,
          behavior: 'smooth'
        });
      });
  });  




  var addressInput = document.getElementById('address')
  if(addressInput){
    addressInput.addEventListener('blur',(e)=> {
      console.log('update meta showing')
      var url = e.target.value;
      var pattern = new RegExp('^(https?:\\/\\/)\\S+$', 'i');

      if (pattern.test(url)) {
        
          url = encodeURIComponent(url);
          link = document.getElementById('meta-update-link')
          if(link){
            link.classList.remove('hidden')
            link.href += '?url=' + url +"&local=True";
          }
      }
    });
  }

  document.getElementById('copyAllButton').addEventListener('click', () => {
    const rows = document.querySelectorAll('.row');
    let copiedContent = '';

    rows.forEach((row) => {
        const linkRow = printLinkRow(row)
        if(linkRow){
          copiedContent += `* ${linkRow}\n`;
        }
    });

    // Copy the content to the clipboard
    navigator.clipboard.writeText(copiedContent);
  });


  //checking if any filters are set to display removeAllFilters element
  const displayElement = document.getElementById('removeAllFilters');
  if(displayElement!==null){
    const hasFilters = document.querySelector('.filter.remove') !== null;
    if (hasFilters) {
      displayElement.style.display = 'inline-block';
    } else {
      displayElement.style.display = 'none';
    }
  }
 
  //settings-menu
  var toggleButton = document.querySelector('.settings-toggle');
  if(toggleButton!==null){
    toggleButton.addEventListener('click', function() {
      var menu = this.nextElementSibling;
      menu.style.display = (menu.style.display === 'block') ? 'none' : 'block';
    });
  }


  document.addEventListener("keydown", function(event) {
  if (event.key === "Escape") {
    const form = document.getElementById("form-container");
    const searchForm = document.getElementById("search-container");

    if (!form.classList.contains("hidden")) {
      form.classList.add("hidden");
      history.back();
    }

    if (!searchForm.classList.contains("hidden")) {
      searchForm.classList.add("hidden");
    }
  }
});

});


function printLinkRow(row){
  if(row===null) return '';
  
  const address = row.querySelector('.address')
  if(address) {
    const link = address.getAttribute('href');
    const comment = row.querySelector('.comment').textContent;
    const summary = row.querySelector('.summary').textContent;
    const content = comment ? comment :  summary ;  
    return `${link} - ${content}`;
  } else {
    console.log('no address found for row '+row)
    return '';
  }
}

function toggleVisibility(container) {
  container.classList.toggle('hidden');
}

function focusFirstInput(container){
  if(container!==null && !container.classList.contains("hidden")){         
    const inputFields = container.getElementsByTagName('input');
    for (let i = 0; i < inputFields.length; i++) { 
        const input = inputFields[i];
        if (input.id!=='csrf_token' && !input.readOnly) {
          input.focus();
          break;
        }
    }    
    const forms = document.querySelectorAll('.forms')    
    for (let i = 0; i < forms.length; i++) { 
      const form = forms[i];      
      if(form!==container){
        form.classList.add('hidden')
      }
    }
  }
}


function confirmMerge(message) {
  return new Promise((resolve, reject) => {
    // Set the confirmation message
    document.getElementById('confirmMessage').textContent = message;

    // Show the modal
    modalElement = document.getElementById('confirmModal')
    modalElement.style.display='block'
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    // Handle the button click events
    const cancelButton = document.getElementById('confirmModal').querySelector('.btn-secondary');
    const confirmButton = document.getElementById('confirmButton');

    cancelButton.addEventListener('click', () => {
      modal.hide();
      resolve(false);
    });

    confirmButton.addEventListener('click', () => {
      modal.hide();
      modalElement = document.getElementById('confirmModal')
      modalElement.style.display='none'
      resolve(true);
    });
  });
}
