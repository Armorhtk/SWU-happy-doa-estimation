import React from "react";
import clsx from "clsx";
import useIsBrowser from "@docusaurus/useIsBrowser";
import { translate } from "@docusaurus/Translate";
import { useColorMode, useThemeConfig } from "@docusaurus/theme-common";
import IconLightMode from "@theme/Icon/LightMode";
import IconDarkMode from "@theme/Icon/DarkMode";

import styles from "./styles.module.css";

function getNextAriaLabel(isDark) {
  return translate(
    {
      message: "Switch to {mode}",
      id: "theme.colorToggle.pill.ariaLabel",
      description: "The ARIA label for the navbar pill color mode toggle",
    },
    {
      mode: isDark
        ? translate({
            message: "light mode",
            id: "theme.colorToggle.pill.mode.light",
            description: "The name for the light color mode",
          })
        : translate({
            message: "dark mode",
            id: "theme.colorToggle.pill.mode.dark",
            description: "The name for the dark color mode",
          }),
    },
  );
}

function getButtonTitle(isDark) {
  return isDark
    ? translate({
        message: "light mode",
        id: "theme.colorToggle.pill.title.light",
        description: "The title for switching to light mode",
      })
    : translate({
        message: "dark mode",
        id: "theme.colorToggle.pill.title.dark",
        description: "The title for switching to dark mode",
      });
}

export default function NavbarColorModeToggle({ className }) {
  const isBrowser = useIsBrowser();
  const { disableSwitch } = useThemeConfig().colorMode;
  const { colorMode, setColorMode } = useColorMode();

  if (disableSwitch) {
    return null;
  }

  const isDark = colorMode === "dark";

  return (
    <div className={clsx(className, styles.toggleItem)}>
      <button
        className={clsx(
          "clean-btn",
          styles.toggleButton,
          isDark && styles.toggleButtonDark,
          !isBrowser && styles.toggleButtonDisabled,
        )}
        type="button"
        onClick={() => setColorMode(isDark ? "light" : "dark")}
        disabled={!isBrowser}
        title={getButtonTitle(isDark)}
        aria-label={getNextAriaLabel(isDark)}
      >
        <span className={clsx(styles.thumb, isDark && styles.thumbDark)}>
          {isDark ? (
            <IconDarkMode aria-hidden className={clsx(styles.icon, styles.iconDark)} />
          ) : (
            <IconLightMode aria-hidden className={clsx(styles.icon, styles.iconLight)} />
          )}
        </span>
      </button>
    </div>
  );
}
