import type * as React from "react";
import { jsx as _jsx, jsxs as _jsxs, Fragment } from "react/jsx-runtime";

function clean(props: any) {
  if (!props) return props;
  let copy: any = null;
  for (const key in props) {
    if (key.startsWith("data-") || key.startsWith("aria-")) {
      if (!copy) copy = { ...props };
      delete copy[key];
    }
  }
  return copy ?? props;
}

export const jsx = (type: any, props: any, key?: any) =>
  _jsx(type, typeof type === "string" ? clean(props) : props, key);
export const jsxs = (type: any, props: any, key?: any) =>
  _jsxs(type, typeof type === "string" ? clean(props) : props, key);
export { Fragment };


export namespace JSX {
  export type ElementType = React.JSX.ElementType;
  export type Element = React.JSX.Element;
  export type ElementClass = React.JSX.ElementClass;
  export type ElementAttributesProperty = React.JSX.ElementAttributesProperty;
  export type ElementChildrenAttribute = React.JSX.ElementChildrenAttribute;
  export type LibraryManagedAttributes<C, P> = React.JSX.LibraryManagedAttributes<C, P>;
  export type IntrinsicAttributes = React.JSX.IntrinsicAttributes;
  export type IntrinsicClassAttributes<T> = React.JSX.IntrinsicClassAttributes<T>;
  export interface IntrinsicElements extends React.JSX.IntrinsicElements {}
}
