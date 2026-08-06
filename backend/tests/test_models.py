"""Testes do modelo de dados."""

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import (
    Instrutor,
    InstrutorDia,
    InstrutorTipologia,
    InstrutorTurno,
    Projeto,
    Tipologia,
    Turno,
)


def _criar_projeto(db: Session, nome: str = "Jovem Digital") -> Projeto:
    projeto = Projeto(nome=nome)
    db.add(projeto)
    db.commit()
    return projeto


def test_instrutor_com_turnos_dias_e_tipologias(db: Session) -> None:
    """Um instrutor multi-turno e multi-tipologia persiste todos os vínculos."""
    projeto = _criar_projeto(db)

    programacao = Tipologia(nome="Programação", carga_horaria_total_horas=60, horas_por_encontro=3)
    pixel_art = Tipologia(nome="Pixel Art", carga_horaria_total_horas=24, horas_por_encontro=2)
    db.add_all([programacao, pixel_art])
    db.commit()

    instrutor = Instrutor(nome="Maria Silva", projeto_id=projeto.id)
    instrutor.turnos = [
        InstrutorTurno(turno=Turno.MANHA_1),
        InstrutorTurno(turno=Turno.NOITE),
    ]
    instrutor.dias = [InstrutorDia(dia_semana=2), InstrutorDia(dia_semana=4)]
    instrutor.tipologias = [
        InstrutorTipologia(tipologia_id=programacao.id),
        InstrutorTipologia(tipologia_id=pixel_art.id),
    ]
    db.add(instrutor)
    db.commit()

    salvo = db.get(Instrutor, instrutor.id)
    assert salvo is not None
    assert salvo.projeto.nome == "Jovem Digital"

    assert {t.turno for t in salvo.turnos} == {Turno.MANHA_1, Turno.NOITE}

    assert sorted(d.dia_semana for d in salvo.dias) == [2, 4]
    assert sorted(v.tipologia.nome for v in salvo.tipologias) == ["Pixel Art", "Programação"]


def test_tipologia_com_nome_duplicado_e_rejeitada(db: Session) -> None:
    db.add(Tipologia(nome="Robótica", carga_horaria_total_horas=40, horas_por_encontro=4))
    db.commit()

    db.add(Tipologia(nome="Robótica", carga_horaria_total_horas=24, horas_por_encontro=2))
    with pytest.raises(IntegrityError):
        db.commit()


def test_instrutor_com_nome_duplicado_e_rejeitado(db: Session) -> None:
    projeto = _criar_projeto(db)
    db.add(Instrutor(nome="João Souza", projeto_id=projeto.id))
    db.commit()

    db.add(Instrutor(nome="João Souza", projeto_id=projeto.id))
    with pytest.raises(IntegrityError):
        db.commit()


def test_turno_duplicado_no_mesmo_instrutor_e_rejeitado(db: Session) -> None:
    projeto = _criar_projeto(db)
    instrutor = Instrutor(nome="Ana Costa", projeto_id=projeto.id)
    instrutor.turnos = [
        InstrutorTurno(turno=Turno.MANHA_1),
        InstrutorTurno(turno=Turno.MANHA_1),
    ]
    db.add(instrutor)

    with pytest.raises(IntegrityError):
        db.commit()


def test_dia_semana_fora_da_faixa_e_rejeitado(db: Session) -> None:
    """Sábado (7) está fora da faixa aceita de segunda (2) a sexta (6)."""
    projeto = _criar_projeto(db)
    instrutor = Instrutor(nome="Carlos Lima", projeto_id=projeto.id)
    instrutor.dias = [InstrutorDia(dia_semana=7)]
    db.add(instrutor)

    with pytest.raises(IntegrityError):
        db.commit()


def test_tipologia_derivada_nasce_pendente(db: Session) -> None:
    """Tipologia sem carga horária configurada bloqueia a simulação."""
    tipologia = Tipologia(nome="Google Workspace")
    db.add(tipologia)
    db.commit()

    assert tipologia.configurada is False
    assert tipologia.num_encontros is None


def test_num_encontros_derivado_da_carga_horaria(db: Session) -> None:
    tipologia = Tipologia(nome="Robótica", carga_horaria_total_horas=40, horas_por_encontro=4)
    db.add(tipologia)
    db.commit()

    assert tipologia.configurada is True
    assert tipologia.num_encontros == 10


def test_carga_horaria_fora_da_faixa_e_rejeitada(db: Session) -> None:
    """A carga horária total precisa ficar entre 24 e 60 horas."""
    db.add(Tipologia(nome="Curso Longo", carga_horaria_total_horas=80, horas_por_encontro=4))

    with pytest.raises(IntegrityError):
        db.commit()
