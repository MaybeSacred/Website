declare const OpaqueTagSymbol: unique symbol;
class OpaqueTag<S extends symbol> {
	private [OpaqueTagSymbol]: S;
}
type _Opaque<T, S extends symbol> = T & OpaqueTag<S>;
export type Opaque<T, S extends symbol> = _Opaque<T, S>;
