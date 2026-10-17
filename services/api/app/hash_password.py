from getpass import getpass

from pwdlib import PasswordHash


def main() -> None:
    password = getpass("Senha do administrador (mínimo 12 caracteres): ")
    confirmation = getpass("Confirme a senha: ")
    if not 12 <= len(password) <= 128:
        raise SystemExit("A senha precisa ter entre 12 e 128 caracteres.")
    if password != confirmation:
        raise SystemExit("As senhas não coincidem.")
    print(PasswordHash.recommended().hash(password))


if __name__ == "__main__":
    main()
