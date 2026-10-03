import { APP_ORIGIN } from "./logic.js";

fetch(`${APP_ORIGIN}/api/state`)
  .then((response) => {
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    location.replace(`${APP_ORIGIN}/`);
  })
  .catch(() => {
    document.getElementById("message").hidden = false;
  });
