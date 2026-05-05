# ============================================================
# SISTEMA INTEGRAL DE GESTIÓN DE CLIENTES, SERVICIOS Y RESERVAS
# Empresa: Software FJ
# Curso: Programación - Fase 4
# ============================================================

from abc import ABC, abstractmethod
from datetime import datetime


# ============================================================
# EXCEPCIONES PERSONALIZADAS
# ============================================================

class ClienteInvalidoError(Exception):
    pass


class ServicioInvalidoError(Exception):
    pass


class ServicioNoDisponibleError(Exception):
    pass


class ReservaInvalidaError(Exception):
    pass


class OperacionNoPermitidaError(Exception):
    pass


# ============================================================
# REGISTRO DE LOGS
# ============================================================

import os

def registrar_log(tipo, mensaje):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    carpeta = os.path.join(base_dir, "Registros")

    if not os.path.exists(carpeta):
        os.makedirs(carpeta)

    ruta = os.path.join(carpeta, "logs.txt")

    with open(ruta, "a", encoding="utf-8") as archivo:
        archivo.write(f"[{fecha_hora}] [{tipo}] {mensaje}\n")


# ============================================================
# CLASE ABSTRACTA GENERAL
# ============================================================

class EntidadSistema(ABC):
    """
    Clase abstracta general para representar entidades del sistema.
    """

    @abstractmethod
    def mostrar_informacion(self):
        pass


# ============================================================
# CLASE CLIENTE
# ============================================================

class Cliente(EntidadSistema):
    """
    Clase que representa un cliente de la empresa Software FJ.
    Aplica encapsulación y validaciones.
    """

    def __init__(self, nombre, documento, correo):
        self.__nombre = None
        self.__documento = None
        self.__correo = None

        self.set_nombre(nombre)
        self.set_documento(documento)
        self.set_correo(correo)

    def set_nombre(self, nombre):
        if not nombre or not nombre.replace(" ", "").isalpha():
            raise ClienteInvalidoError("El nombre del cliente solo debe contener letras.")
        self.__nombre = nombre

    def set_documento(self, documento):
        if not documento or not documento.isdigit():
            raise ClienteInvalidoError("El documento del cliente solo debe contener números.")
        self.__documento = documento

    def set_correo(self, correo):
        if "@" not in correo or "." not in correo:
            raise ClienteInvalidoError("El correo electrónico no es válido.")
        self.__correo = correo

    def get_nombre(self):
        return self.__nombre

    def get_documento(self):
        return self.__documento

    def get_correo(self):
        return self.__correo

    def mostrar_informacion(self):
        return f"Cliente: {self.__nombre} | Documento: {self.__documento} | Correo: {self.__correo}"


# ============================================================
# CLASE ABSTRACTA SERVICIO
# ============================================================

class Servicio(EntidadSistema):
    """
    Clase abstracta para representar los servicios generales.
    """

    def __init__(self, nombre, costo_base, disponible=True):
        if not nombre:
            raise ServicioInvalidoError("El nombre del servicio no puede estar vacío.")

        if costo_base <= 0:
            raise ServicioInvalidoError("El costo base debe ser mayor que cero.")

        self.nombre = nombre
        self.costo_base = costo_base
        self.disponible = disponible

    @abstractmethod
    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        pass

    @abstractmethod
    def descripcion(self):
        pass

    def validar_disponibilidad(self):
        if not self.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self.nombre}' no está disponible.")

    def mostrar_informacion(self):
        return self.descripcion()


# ============================================================
# CLASES DERIVADAS DE SERVICIO
# ============================================================

class ServicioSala(Servicio):
    """
    Servicio para reserva de salas.
    """

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        if duracion <= 0:
            raise ServicioInvalidoError("La duración debe ser mayor que cero.")

        subtotal = self.costo_base * duracion
        total = subtotal + (subtotal * impuesto / 100) - (subtotal * descuento / 100)
        return total

    def descripcion(self):
        return f"Servicio de reserva de sala: {self.nombre} | Costo base: ${self.costo_base}"


class AlquilerEquipo(Servicio):
    """
    Servicio para alquiler de equipos.
    """

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        if duracion <= 0:
            raise ServicioInvalidoError("La duración debe ser mayor que cero.")

        seguro = 20000
        subtotal = (self.costo_base * duracion) + seguro
        total = subtotal + (subtotal * impuesto / 100) - (subtotal * descuento / 100)
        return total

    def descripcion(self):
        return f"Servicio de alquiler de equipo: {self.nombre} | Costo base: ${self.costo_base}"


class AsesoriaEspecializada(Servicio):
    """
    Servicio para asesorías especializadas.
    """

    def calcular_costo(self, duracion, impuesto=0, descuento=0):
        if duracion <= 0:
            raise ServicioInvalidoError("La duración debe ser mayor que cero.")

        tarifa_profesional = 50000
        subtotal = (self.costo_base * duracion) + tarifa_profesional
        total = subtotal + (subtotal * impuesto / 100) - (subtotal * descuento / 100)
        return total

    def descripcion(self):
        return f"Servicio de asesoría especializada: {self.nombre} | Costo base: ${self.costo_base}"


# ============================================================
# CLASE RESERVA
# ============================================================

class Reserva(EntidadSistema):
    """
    Clase que representa una reserva dentro del sistema.
    """

    def __init__(self, cliente, servicio, duracion):
        if not isinstance(cliente, Cliente):
            raise ReservaInvalidaError("El cliente asignado no es válido.")

        if not isinstance(servicio, Servicio):
            raise ReservaInvalidaError("El servicio asignado no es válido.")

        if duracion <= 0:
            raise ReservaInvalidaError("La duración de la reserva debe ser mayor que cero.")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"

    def confirmar(self):
        try:
            self.servicio.validar_disponibilidad()
        except ServicioNoDisponibleError as error:
            raise ReservaInvalidaError("No se puede confirmar la reserva porque el servicio no está disponible.") from error
        else:
            self.estado = "Confirmada"
            registrar_log("INFO", "Reserva confirmada correctamente.")

    def cancelar(self):
        if self.estado == "Cancelada":
            raise OperacionNoPermitidaError("La reserva ya se encuentra cancelada.")

        self.estado = "Cancelada"
        registrar_log("INFO", "Reserva cancelada correctamente.")

    def procesar_reserva(self, impuesto=0, descuento=0):
        try:
            if self.estado != "Confirmada":
                raise ReservaInvalidaError("La reserva debe estar confirmada antes de procesarse.")

            total = self.servicio.calcular_costo(self.duracion, impuesto, descuento)

        except ReservaInvalidaError as error:
            registrar_log("ERROR", str(error))
            raise

        except Exception as error:
            registrar_log("ERROR", f"Error inesperado al procesar reserva: {error}")
            raise

        else:
            registrar_log("INFO", f"Reserva procesada correctamente. Total: ${total}")
            return total

        finally:
            registrar_log("INFO", "Finalizó el intento de procesamiento de reserva.")

    def mostrar_informacion(self):
        return (
            f"Reserva | Cliente: {self.cliente.get_nombre()} | "
            f"Servicio: {self.servicio.nombre} | "
            f"Duración: {self.duracion} horas | Estado: {self.estado}"
        )


# ============================================================
# FUNCIÓN PARA EJECUTAR OPERACIONES DE PRUEBA
# ============================================================

def ejecutar_operacion(numero, descripcion, funcion):
    """
    Ejecuta una operación usando manejo avanzado de excepciones.
    """
    print(f"\nOPERACIÓN {numero}: {descripcion}")

    try:
        resultado = funcion()

    except Exception as error:
        print(f"Error controlado: {error}")
        registrar_log("ERROR", f"Operación {numero}: {error}")

    else:
        if resultado is not None:
            print(resultado)
        print("Operación ejecutada correctamente.")
        registrar_log("INFO", f"Operación {numero} ejecutada correctamente.")

    finally:
        print("Fin de la operación.")


# ============================================================
# SIMULACIÓN DE 10 OPERACIONES COMPLETAS
# ============================================================

def main():
    print("================================================")
    print(" SISTEMA SOFTWARE FJ - CLIENTES, SERVICIOS Y RESERVAS ")
    print("================================================")

    # 1. Cliente válido
    ejecutar_operacion(
        1,
        "Registrar cliente válido",
        lambda: Cliente("Juan Perez", "123456789", "juan@gmail.com").mostrar_informacion()
    )

    # 2. Cliente inválido por documento con letras
    ejecutar_operacion(
        2,
        "Registrar cliente inválido con documento incorrecto",
        lambda: Cliente("Maria Lopez", "ABC123", "maria@gmail.com")
    )

    # 3. Cliente inválido por correo incorrecto
    ejecutar_operacion(
        3,
        "Registrar cliente inválido con correo incorrecto",
        lambda: Cliente("Carlos Ruiz", "987654321", "carloscorreo.com")
    )

    # 4. Crear servicio de sala válido
    ejecutar_operacion(
        4,
        "Crear servicio de reserva de sala",
        lambda: ServicioSala("Sala de reuniones A", 80000).descripcion()
    )

    # 5. Crear servicio inválido con costo negativo
    ejecutar_operacion(
        5,
        "Crear servicio inválido con costo negativo",
        lambda: ServicioSala("Sala defectuosa", -50000)
    )

    # 6. Reserva exitosa
    def operacion_reserva_exitosa():
        cliente = Cliente("Ana Torres", "11223344", "ana@gmail.com")
        servicio = ServicioSala("Sala VIP", 100000)
        reserva = Reserva(cliente, servicio, 2)
        reserva.confirmar()
        total = reserva.procesar_reserva(impuesto=19, descuento=10)
        return f"{reserva.mostrar_informacion()} | Total: ${total:.2f}"

    ejecutar_operacion(
        6,
        "Crear y procesar reserva exitosa",
        operacion_reserva_exitosa
    )

    # 7. Reserva fallida por duración inválida
    ejecutar_operacion(
        7,
        "Crear reserva con duración inválida",
        lambda: Reserva(
            Cliente("Luis Gomez", "55667788", "luis@gmail.com"),
            ServicioSala("Sala B", 70000),
            -3
        )
    )

    # 8. Reserva fallida por servicio no disponible
    def operacion_servicio_no_disponible():
        cliente = Cliente("Sofia Diaz", "99887766", "sofia@gmail.com")
        servicio = AlquilerEquipo("Video Beam", 60000, disponible=False)
        reserva = Reserva(cliente, servicio, 1)
        reserva.confirmar()
        return reserva.mostrar_informacion()

    ejecutar_operacion(
        8,
        "Intentar confirmar reserva con servicio no disponible",
        operacion_servicio_no_disponible
    )

    # 9. Reserva cancelada
    def operacion_reserva_cancelada():
        cliente = Cliente("Deiver Legarda", "44332211", "deiverlegarda@gmail.com")
        servicio = AsesoriaEspecializada("Asesoría Python", 120000)
        reserva = Reserva(cliente, servicio, 1)
        reserva.confirmar()
        reserva.cancelar()
        return reserva.mostrar_informacion()

    ejecutar_operacion(
        9,
        "Crear y cancelar una reserva",
        operacion_reserva_cancelada
    )

    # 10. Intentar procesar reserva sin confirmar
    def operacion_procesar_sin_confirmar():
        cliente = Cliente("Valentina Chaves", "10101010", "valentinachaves@gmail.com")
        servicio = ServicioSala("Sala C", 75000)
        reserva = Reserva(cliente, servicio, 1)
        total = reserva.procesar_reserva()
        return f"Total: ${total:.2f}"

    ejecutar_operacion(
        10,
        "Procesar reserva sin confirmar",
        operacion_procesar_sin_confirmar
    )

    # 11. Alquiler de equipo exitoso
    def operacion_alquiler_equipo():
        cliente = Cliente("Santiago Jimenez", "20202020", "santiagojimenez@gmail.com")
        servicio = AlquilerEquipo("Portátil Lenovo", 50000)
        reserva = Reserva(cliente, servicio, 3)
        reserva.confirmar()
        total = reserva.procesar_reserva(impuesto=19, descuento=5)
        return f"{reserva.mostrar_informacion()} | Total: ${total:.2f}"

    ejecutar_operacion(
        11,
        "Procesar alquiler de equipo exitoso",
        operacion_alquiler_equipo
    )

    print("\n================================================")
    print("Simulación finalizada. Revise el archivo Registros/logs.txt")
    print("================================================")


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

if __name__ == "__main__":
    main()

