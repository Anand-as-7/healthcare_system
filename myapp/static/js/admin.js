tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        tertiary: "#00525a",
        "on-tertiary-container": "#82edfc",
        "on-primary-fixed-variant": "#003dab",
        "on-background": "#151c27",
        "inverse-surface": "#2a313d",
        "on-primary-container": "#d4dcff",
        "primary-fixed": "#dbe1ff",
        "surface-tint": "#1353d8",
        "surface-container-highest": "#dce2f3",
        "primary-fixed-dim": "#b5c4ff",
        "on-secondary-fixed": "#25005a",
        "on-secondary": "#ffffff",
        "error-container": "#ffdad6",
        "surface-container-lowest": "#ffffff",
        "on-primary-fixed": "#00174d",
        "surface-container-low": "#f0f3ff",
        "surface-container": "#e7eefe",
        "on-tertiary": "#ffffff",
        background: "#f9f9ff",
        "surface-container-high": "#e2e8f8",
        "on-tertiary-fixed-variant": "#004f57",
        "on-tertiary-fixed": "#001f23",
        "tertiary-container": "#006c77",
        "surface-dim": "#d3daea",
        "inverse-primary": "#b5c4ff",
        "on-error": "#ffffff",
        error: "#ba1a1a",
        "secondary-fixed": "#eaddff",
        "surface-bright": "#f9f9ff",
        "on-surface": "#151c27",
        "on-surface-variant": "#434654",
        "secondary-fixed-dim": "#d2bbff",
        "tertiary-fixed": "#92f1ff",
        surface: "#f9f9ff",
        "secondary-container": "#8b4aff",
        "inverse-on-surface": "#ebf1ff",
        "on-primary": "#ffffff",
        "tertiary-fixed-dim": "#6ad6e5",
        "primary-container": "#1a56db",
        secondary: "#7127e5",
        "surface-variant": "#dce2f3",
        "on-secondary-container": "#fffbff",
        primary: "#003fb1",
        "outline-variant": "#c3c5d7",
        "on-secondary-fixed-variant": "#5a00c6",
        outline: "#737686",
        "on-error-container": "#93000a"
      },

      borderRadius: {
        DEFAULT: "0.25rem",
        lg: "0.5rem",
        xl: "0.75rem",
        full: "9999px"
      },

      spacing: {
        "section-padding": "64px",
        "margin-desktop": "48px",
        "stack-sm": "8px",
        "stack-md": "16px",
        gutter: "24px",
        "container-max": "1440px",
        "margin-mobile": "16px",
        unit: "8px",
        "stack-lg": "32px"
      },

      fontFamily: {
        "body-sm": ["Inter"],
        "display-lg": ["Inter"],
        "label-md": ["Inter"],
        "label-sm": ["Inter"],
        "headline-lg-mobile": ["Inter"],
        "headline-sm": ["Inter"],
        "body-md": ["Inter"],
        "headline-lg": ["Inter"],
        "headline-md": ["Inter"],
        "body-lg": ["Inter"]
      },

      fontSize: {
        "body-sm": ["14px", { lineHeight: "20px", fontWeight: "400" }],
        "display-lg": ["48px", { lineHeight: "60px", letterSpacing: "-0.02em", fontWeight: "700" }],
        "label-md": ["14px", { lineHeight: "20px", letterSpacing: "0.05em", fontWeight: "600" }],
        "label-sm": ["12px", { lineHeight: "16px", fontWeight: "500" }],
        "headline-lg-mobile": ["28px", { lineHeight: "36px", fontWeight: "700" }],
        "headline-sm": ["20px", { lineHeight: "28px", fontWeight: "600" }],
        "body-md": ["16px", { lineHeight: "24px", fontWeight: "400" }],
        "headline-lg": ["32px", { lineHeight: "40px", letterSpacing: "-0.01em", fontWeight: "700" }],
        "headline-md": ["24px", { lineHeight: "32px", fontWeight: "600" }],
        "body-lg": ["18px", { lineHeight: "28px", fontWeight: "400" }]
      }
    }
  }
};

document.addEventListener("DOMContentLoaded", function () {
  // Micro-interaction for sidebar links
  document.querySelectorAll("nav a").forEach(function (link) {
    link.addEventListener("click", function () {
      if (window.innerWidth >= 768) {
        document.querySelectorAll("nav a").forEach(function (item) {
          item.classList.remove(
            "text-primary",
            "dark:text-primary-fixed",
            "font-bold",
            "border-r-4",
            "border-primary",
            "dark:border-primary-fixed",
            "bg-primary/5"
          );

          item.classList.add("text-on-surface-variant", "dark:text-outline");
        });

        this.classList.add(
          "text-primary",
          "dark:text-primary-fixed",
          "font-bold",
          "border-r-4",
          "border-primary",
          "dark:border-primary-fixed",
          "bg-primary/5"
        );

        this.classList.remove("text-on-surface-variant", "dark:text-outline");
      }
    });
  });

  // Simple data-refresh animation simulation
  setInterval(function () {
    const uptime = document.querySelector("h3");

    if (uptime && uptime.innerText.includes("99.98")) {
      const newVal = (99.98 + Math.random() * 0.01).toFixed(2);

      // Disabled to keep UI static
      // uptime.innerText = newVal + "%";
    }
  }, 5000);
});