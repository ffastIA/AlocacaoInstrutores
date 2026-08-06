import { Button } from "./Button";
import { Modal } from "./Modal";
import styles from "./ConfirmDialog.module.css";

interface ConfirmDialogProps {
  aberto: boolean;
  titulo: string;
  mensagem: string;
  confirmando?: boolean;
  onConfirmar: () => void;
  onCancelar: () => void;
}

/** Confirmação de intenção antes de uma ação destrutiva. */
export function ConfirmDialog({
  aberto,
  titulo,
  mensagem,
  confirmando = false,
  onConfirmar,
  onCancelar,
}: ConfirmDialogProps) {
  return (
    <Modal aberto={aberto} titulo={titulo} onFechar={onCancelar}>
      <p>{mensagem}</p>
      <div className={styles.acoes}>
        <Button variante="secundaria" onClick={onCancelar} disabled={confirmando}>
          Cancelar
        </Button>
        <Button variante="destrutiva" onClick={onConfirmar} carregando={confirmando}>
          Remover
        </Button>
      </div>
    </Modal>
  );
}
