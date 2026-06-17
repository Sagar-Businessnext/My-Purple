# Common Build Errors and Fixes

## TypeScript

| Error | Cause | Fix |
|-------|-------|-----|
| `Cannot find module 'X'` | Missing dependency or wrong import path | `npm install X` or fix the import path |
| `TS2307: Cannot find module './X'` | Wrong relative path or missing file | Check file exists, check path casing |
| `TS2339: Property 'X' does not exist on type 'Y'` | Missing property in interface | Add property to interface or use type guard |
| `TS2345: Argument of type 'X' is not assignable to type 'Y'` | Type mismatch | Fix the type — don't cast to `any` |
| `TS2532: Object is possibly 'undefined'` | Unguarded nullable access | Add null check or optional chaining |
| `TS7006: Parameter 'X' implicitly has an 'any' type` | Missing type annotation | Add explicit type |
| `TS1259: Module 'X' can only be default-imported using 'esModuleInterop'` | CJS/ESM interop | Enable `esModuleInterop` in tsconfig or use `import * as X` |

## .NET

| Error | Cause | Fix |
|-------|-------|-----|
| `CS0246: The type or namespace name 'X' could not be found` | Missing using or package | Add `using` directive or install NuGet package |
| `CS1061: 'X' does not contain a definition for 'Y'` | Wrong type or missing method | Check the type, add method, or fix reference |
| `CS0103: The name 'X' does not exist in the current context` | Missing variable or import | Declare variable or add using |

## Python

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'X'` | Missing package | `pip install X` or fix import |
| `ImportError: cannot import name 'X' from 'Y'` | Wrong import | Check the module's exports |
| `SyntaxError` | Malformed code | Check indentation, brackets, colons |
| `TypeError: 'X' object is not callable` | Wrong usage | Check if it's a property vs method |

## General

| Issue | Cause | Fix |
|-------|-------|-----|
| Circular dependency | Module A imports B which imports A | Extract shared code to a third module |
| Version conflict | Incompatible dependency versions | Check peer dependencies, align versions |
| Missing env variable | Config expects env var at build time | Set the variable or add a default |
