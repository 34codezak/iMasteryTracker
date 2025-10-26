export default class SidebarController {
  constructor({ heroActions, menuToggle, sidebarBackdrop }, mobileMedia) {
    this.panel = heroActions ?? null;
    this.toggleBtn = menuToggle ?? null;
    this.backdrop = sidebarBackdrop ?? null;
    this.mobileMedia = mobileMedia ?? null;
    this.open = false;

    this.handleResize = () => this.sync();
    this.handleMediaChange = () => this.toggle(false);
  }

  init() {
    if (!this.panel || !this.toggleBtn) {
      return;
    }

    this.toggleBtn.addEventListener("click", () => this.toggle());
    this.backdrop?.addEventListener("click", () => this.toggle(false));
    document.addEventListener("keydown", this.onKeydown);
    window.addEventListener("resize", this.handleResize);

    if (this.mobileMedia) {
      if (typeof this.mobileMedia.addEventListener === "function") {
        this.mobileMedia.addEventListener("change", this.handleMediaChange);
      } else if (typeof this.mobileMedia.addListener === "function") {
        this.mobileMedia.addListener(this.handleMediaChange);
      }
    }

    this.sync();
  }

  sync() {
    if (!this.panel || !this.toggleBtn) return;

    const toggleVisible = this.toggleBtn.offsetParent !== null;
    if (!toggleVisible && this.open) {
      this.open = false;
    }

    this.applyAttrs();
  }

  toggle(force) {
    if (!this.panel || !this.toggleBtn) return;

    const toggleVisible = this.toggleBtn.offsetParent !== null;
    const nextState = typeof force === "boolean" ? force : !this.open;
    this.open = toggleVisible ? nextState : false;
    this.applyAttrs();
  }

  applyAttrs() {
    if (!this.panel || !this.toggleBtn) return;

    const toggleVisible = this.toggleBtn.offsetParent !== null;
    const isOpen = toggleVisible ? this.open : false;
    const shouldHide = toggleVisible ? !isOpen : false;

    this.panel.classList.toggle("is-open", isOpen);
    this.panel.setAttribute("aria-hidden", String(shouldHide));

    if (this.backdrop) {
      if (isOpen) {
        this.backdrop.removeAttribute("hidden");
      } else {
        this.backdrop.setAttribute("hidden", "");
      }
      this.backdrop.classList.toggle("is-active", isOpen);
      this.backdrop.setAttribute("aria-hidden", String(!isOpen));
    }

    const icon = this.toggleBtn.querySelector("i");
    if (icon) {
      icon.classList.toggle("fa-bars", !isOpen);
      icon.classList.toggle("fa-xmark", isOpen);
    }

    this.toggleBtn.setAttribute("aria-expanded", String(isOpen));
    this.toggleBtn.setAttribute(
      "aria-label",
      isOpen ? "Close sidebar menu" : "Open sidebar menu"
    );

    document.body.classList.toggle("sidebar-open", isOpen);
  }

  onKeydown = event => {
    if (event.key === "Escape" && this.open) {
      this.toggle(false);
      this.toggleBtn.focus();
    }
  };
}

