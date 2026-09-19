import type * as React from "react";
import { jsxDEV as _jsxDEV } from "react/jsx-dev-runtime";
import { Fragment } from "react/jsx-runtime";

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

export const jsxDEV = (
  type: any,
  props: any,
  key: any,
  isStatic: boolean,
  source?: any,
  self?: any,
) => _jsxDEV(type, typeof type === "string" ? clean(props) : props, key, isStatic, source, self);
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
