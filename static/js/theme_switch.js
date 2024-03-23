const themeSwitch = document.getElementById("theme-switch");

window.onload = checkTheme();

function checkTheme() {
  const localStorageTheme = localStorage.getItem("theme");
  if (localStorageTheme === "dark") {
    document.documentElement.setAttribute("data-theme", "dark");
    themeSwitch.checked = true;
  }
}

function switchTheme() {
  if (this.checked) {
    document.documentElement.setAttribute("data-theme", "dark");
    localStorage.setItem("theme", "dark");
  } else {
    document.documentElement.setAttribute("data-theme", "light");
    localStorage.setItem("theme", "light");
  }
}
themeSwitch.addEventListener("click", switchTheme);
