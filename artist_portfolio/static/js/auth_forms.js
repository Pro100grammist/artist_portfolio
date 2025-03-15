document.addEventListener('DOMContentLoaded', function() {
    const usernameField = document.querySelector('input[name="username"]');
    const helpText = document.createElement('span');
    helpText.style.display = 'none';
    helpText.style.color = 'red';
    helpText.textContent = 'Invalid character entered. Only letters, digits and @/./+/-/_ are allowed.';
    usernameField.parentNode.appendChild(helpText);

    usernameField.addEventListener('input', function() {
        const pattern = new RegExp(usernameField.getAttribute('pattern'));
        if (!pattern.test(usernameField.value)) {
            helpText.style.display = 'block';
        } else {
            helpText.style.display = 'none';
        }
    });
});
