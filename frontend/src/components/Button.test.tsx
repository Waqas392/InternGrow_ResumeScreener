import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, expect, test } from "vitest";
import { Button } from "./Button";

afterEach(() => {
  cleanup();
});

test("renders button label", () => {
  render(<Button>Save</Button>);
  expect(screen.getByText("Save")).toBeTruthy();
});

test("shows loading state", () => {
  render(<Button loading>Save</Button>);
  expect(screen.getByRole("button").hasAttribute("disabled")).toBe(true);
});
