// Tab title counter + red favicon badge (drawn on a canvas over CPIN.JK.png).
const FAVICON_SRC = "/CPIN.JK.png";
const BASE_TITLE = "Safety Dashboard";

let baseImg = null;

function loadBase() {
  return new Promise((resolve) => {
    if (baseImg && baseImg.complete && baseImg.naturalWidth) return resolve(baseImg);
    const img = new Image();
    img.onload = () => {
      baseImg = img;
      resolve(img);
    };
    img.onerror = () => resolve(null);
    img.src = FAVICON_SRC;
  });
}

function setFaviconHref(href) {
  let link = document.getElementById("app-favicon");
  if (!link) {
    link = document.createElement("link");
    link.id = "app-favicon";
    link.rel = "icon";
    document.head.appendChild(link);
  }
  link.href = href;
}

// Update both the document title and the favicon with the unread count.
export async function updateBadge(count) {
  const n = Math.max(0, count | 0);
  document.title = n > 0 ? `(${n > 99 ? "99+" : n}) ${BASE_TITLE}` : BASE_TITLE;

  if (n <= 0) {
    setFaviconHref(FAVICON_SRC);
    return;
  }

  const img = await loadBase();
  const size = 64;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d");
  if (img) ctx.drawImage(img, 0, 0, size, size);

  const label = n > 99 ? "99+" : String(n);
  const r = 21;
  const cx = size - r - 1;
  const cy = r + 1;

  ctx.beginPath();
  ctx.arc(cx, cy, r, 0, 2 * Math.PI);
  ctx.fillStyle = "#ef4444";
  ctx.fill();
  ctx.lineWidth = 4;
  ctx.strokeStyle = "#ffffff";
  ctx.stroke();

  ctx.fillStyle = "#ffffff";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.font = `bold ${label.length >= 3 ? 22 : 30}px Arial, sans-serif`;
  ctx.fillText(label, cx, cy + 1);

  try {
    setFaviconHref(canvas.toDataURL("image/png"));
  } catch (e) {
    setFaviconHref(FAVICON_SRC);
  }
}
