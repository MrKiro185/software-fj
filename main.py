
from abc import ABC, abstractmethod
import datetime

# ---------- Excepciones personalizadas ----------
class ErrorSistema(Exception):
    pass

class DatoInvalido(ErrorSistema):
    pass

class ServicioNoDisponible(ErrorSistema):
    pass

class ReservaIncorrecta(ErrorSistema):
    pass

def registrar_log(mensaje):
    try:
        with open("logs.txt", "a", encoding="utf-8") as archivo:
            hora = datetime.datetime.now()
            archivo.write(f"[{hora}] {mensaje}\n")
    except Exception as e:
        print("No se pudo escribir el log:", e)
    finally:
        pass

# ---------- Clase abstracta general ----------
class Entidad(ABC):
    def __init__(self, id_entidad):
        self._id = id_entidad

    @abstractmethod
    def describir(self):
        pass

    @property
    def id(self):
        return self._id

# ---------- Cliente ----------
class Cliente(Entidad):
    def __init__(self, id_cliente, nombre, correo, edad):
        super().__init__(id_cliente)
        if not nombre or len(nombre.strip()) == 0:
            raise DatoInvalido("El nombre no puede estar vacio")
        if "@" not in correo:
            raise DatoInvalido("Correo invalido, debe tener @")
        if edad < 0 or edad > 120:
            raise DatoInvalido("Edad invalida")
        self.__nombre = nombre
        self.__correo = correo
        self.__edad = edad

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    def describir(self):
        return f"Cliente {self.id}: {self.__nombre} - {self.__correo}"

# ---------- Servicio abstracto ----------
class Servicio(ABC):
    def __init__(self, codigo, nombre, precio_base, disponible=True):
        self.codigo = codigo
        self.nombre = nombre
        self.precio_base = precio_base
        self.disponible = disponible

    @abstractmethod
    def calcular_costo(self, duracion=1, impuesto=0, descuento=0):
        pass

    @abstractmethod
    def describir(self):
        pass

    def validar(self):
        if self.precio_base <= 0:
            raise DatoInvalido("El precio debe ser mayor a 0")
        if not self.disponible:
            raise ServicioNoDisponible(f"Servicio {self.nombre} no disponible")

# ---------- 3 Servicios especializados ----------
class ReservaSala(Servicio):
    def calcular_costo(self, duracion=1, impuesto=0, descuento=0):
        try:
            self.validar()
            total = (self.precio_base * duracion) + impuesto - descuento
            if total < 0:
                raise DatoInvalido("El total no puede ser negativo")
        except DatoInvalido as e:
            raise ReservaIncorrecta("Error en reserva de sala") from e
        else:
            registrar_log(f"Costo sala calculado: {total}")
            return total
        finally:
            pass

    def describir(self):
        return f"Sala: {self.nombre} - ${self.precio_base}/hora"

class AlquilerEquipo(Servicio):
    def calcular_costo(self, duracion=1, impuesto=0, descuento=0):
        self.validar()
        total = (self.precio_base * duracion) + impuesto - descuento
        return total

    def describir(self):
        return f"Equipo: {self.nombre} - ${self.precio_base}/dia"

class Asesoria(Servicio):
    def calcular_costo(self, duracion=1, impuesto=0, descuento=0):
        self.validar()
        if duracion <= 0:
            raise DatoInvalido("Duracion invalida para asesoria")
        total = (self.precio_base * duracion) + impuesto - descuento
        return total

    def describir(self):
        return f"Asesoria: {self.nombre} - ${self.precio_base}/hora"

# ---------- Reserva ----------
class Reserva(Entidad):
    def __init__(self, id_reserva, cliente, servicio, duracion):
        super().__init__(id_reserva)
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"

    def describir(self):
        return f"Reserva {self.id} - {self.cliente.nombre} - {self.servicio.nombre} - {self.estado}"

    def confirmar(self):
        try:
            if self.duracion <= 0:
                raise ReservaIncorrecta("Duracion debe ser mayor a 0")
            costo = self.servicio.calcular_costo(self.duracion)
            self.estado = "Confirmada"
            print(f"Reserva confirmada: {self.describir()} - Costo: ${costo}")
            registrar_log(f"Reserva {self.id} confirmada")
        except Exception as e:
            self.estado = "Fallida"
            registrar_log(f"Error en reserva {self.id}: {e}")
            print(f"Error al confirmar reserva: {e}")

    def cancelar(self):
        try:
            if self.estado == "Cancelada":
                raise ReservaIncorrecta("Ya esta cancelada")
            self.estado = "Cancelada"
            print(f"Reserva {self.id} cancelada")
        except Exception as e:
            registrar_log(f"Error al cancelar: {e}")
            print(f"Error: {e}")
        finally:
            print("Proceso de cancelacion terminado")

# ---------- Programa principal - 10 operaciones ----------
def main():
    print("=== SOFTWARE FJ - Sistema Integral ===")
    clientes = []
    servicios = []
    reservas = []

    # Operacion 1 y 2: clientes validos
    try:
        c1 = Cliente(1, "Juan Perez", "juan@gmail.com", 25)
        c2 = Cliente(2, "Ana Gomez", "ana@gmail.com", 30)
        clientes.append(c1)
        clientes.append(c2)
        print(c1.describir())
        print(c2.describir())
    except DatoInvalido as e:
        print("Error cliente:", e)
        registrar_log(str(e))

    # Operacion 3: cliente invalido
    try:
        c_malo = Cliente(3, "", "sinarroba.com", 200)
        clientes.append(c_malo)
    except DatoInvalido as e:
        print("Cliente invalido detectado:", e)
        registrar_log(f"Cliente invalido: {e}")
    else:
        print("Cliente creado sin errores")
    finally:
        print("Validacion de clientes terminada")

    # Operacion 4,5,6: crear servicios
    try:
        s1 = ReservaSala(101, "Sala A", 50000)
        s2 = AlquilerEquipo(102, "Proyector", 80000)
        s3 = Asesoria(103, "Asesoria Python", 120000)
        servicios.extend([s1, s2, s3])
        for s in servicios:
            print(s.describir())
    except Exception as e:
        print("Error servicio:", e)

    # Operacion 7: servicio no disponible
    try:
        s_malo = ReservaSala(104, "Sala B", 60000, disponible=False)
        s_malo.validar()
    except ServicioNoDisponible as e:
        print("Servicio no disponible:", e)
        registrar_log(str(e))

    # Operacion 8,9,10: reservas
    try:
        r1 = Reserva(1, c1, s1, 2)
        r1.confirmar()
        reservas.append(r1)

        r2 = Reserva(2, c2, s2, 1)
        r2.confirmar()
        reservas.append(r2)

        r3 = Reserva(3, c1, s3, 0)  # esta va a fallar
        r3.confirmar()
        reservas.append(r3)
    except Exception as e:
        print("Error general en reservas:", e)
        registrar_log(str(e))

    # Cancelar una
    r1.cancelar()

    print("\n--- Resumen final ---")
    for r in reservas:
        print(r.describir())
    print("Sistema termino sin caerse. Revisa logs.txt")

if __name__ == "__main__":
    main()
