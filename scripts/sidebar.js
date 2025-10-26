export default class SidebarController {
  constructor({ heroActions, menuToggle, sidebarBackdrop }, mobileMedia) {
    this.panel = heroActions ?? null;
    this.toggleBtn = menuToggle ?? null;
    this.backdrop = sidebarBackdrop ?? null;
    this.mobileMedia = mobileMedia ?? null;

    const hasPanelOpen = this.panel?.classList?.contains("is-open");
    const toggleExpanded = this.toggleBtn?.getAttribute("aria-expanded") === "true";
    const bodyOpen =
      typeof document !== "undefined" &&
      document.body?.classList?.contains("sidebar-open");
    this.open = Boolean(hasPanelOpen || toggleExpanded || bodyOpen);

    this._resizeTimeout = null;

    this.handleToggleClick = () => this.toggle();
    this.handleBackdropClick = () => this.toggle(false);
    this.handleMediaChange = () => this.toggle(false);
    this.handleKeydown = event => {
      if (event.key === "Escape" && this.open) {
        this.toggle(false);
        this.toggleBtn?.focus();
      }
    };
    this.handleResize = () => {
      if (this._resizeTimeout) {
        clearTimeout(this._resizeTimeout);
      }
      this._resizeTimeout = setTimeout(() => {
        this._resizeTimeout = null;
        this.sync();
      }, 150);
    };

    this.initialized = false;
  }

  init() {
    if (this.initialized || !this.panel || !this.toggleBtn) {
      return;
    }

    this.toggleBtn.addEventListener("click", this.handleToggleClick);
    this.backdrop?.addEventListener("click", this.handleBackdropClick);
    document.addEventListener("keydown", this.handleKeydown);
    window.addEventListener("resize", this.handleResize);

    if (this.mobileMedia) {
      if (typeof this.mobileMedia.addEventListener === "function") {
        this.mobileMedia.addEventListener("change", this.handleMediaChange);
      } else if (typeof this.mobileMedia.addListener === "function") {
        this.mobileMedia.addListener(this.handleMediaChange);
      }
    }

    this.initialized = true;
    this.sync();
  }

  destroy() {
    if (!this.initialized) {
      return;
    }

    this.toggleBtn?.removeEventListener("click", this.handleToggleClick);
    this.backdrop?.removeEventListener("click", this.handleBackdropClick);
    document.removeEventListener("keydown", this.handleKeydown);
    window.removeEventListener("resize", this.handleResize);

    if (this.mobileMedia) {
      if (typeof this.mobileMedia.removeEventListener === "function") {
        this.mobileMedia.removeEventListener("change", this.handleMediaChange);
      } else if (typeof this.mobileMedia.removeListener === "function") {
        this.mobileMedia.removeListener(this.handleMediaChange);
      }
    }

    if (this._resizeTimeout) {
      clearTimeout(this._resizeTimeout);
      this._resizeTimeout = null;
    }

    this.toggle(false);
    this.initialized = false;
  }

  sync() {
    this._update(this.open);
  }

  toggle(force) {
    this._update(force);
  }

  _update(force) {
    if (!this.panel || !this.toggleBtn) {
      return;
    }

    const toggleVisible = this._isToggleVisible();
    const nextState = typeof force === "boolean" ? force : !this.open;
    this.open = toggleVisible ? nextState : false;

    const isOpen = toggleVisible && this.open;
    const shouldHide = toggleVisible ? !isOpen : false;

    this.panel.classList.toggle("is-open", isOpen);
    this.panel.setAttribute("aria-hidden", String(shouldHide));

    if (this.backdrop) {
      this.backdrop.hidden = !isOpen;
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

  _isToggleVisible() {
    if (!this.toggleBtn) {
      return false;
    }

    const style = window.getComputedStyle(this.toggleBtn);
    return (
      style.display !== "none" &&
      style.visibility !== "hidden" &&
      parseFloat(style.opacity) > 0
    );
  }
}

