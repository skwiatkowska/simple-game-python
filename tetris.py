import pygame, sys
from random import randrange as rand


kolory = [(238, 233, 233), #biały
        (153, 0, 153), #fioletowy
        (51, 51, 255), #niebieski
        (51, 153, 255), # jasnoniebieski
        (255, 102, 255), #jasnorozowy
        (255, 0, 255), #rozowy
        (238, 233, 233), #bialy
        (204, 0, 102), #fuksja
        (12, 12, 12), #tło
]

rozmiarKomorek = 35
kolumny = 12
wiersze = 15


ksztalty = [
    [[1, 1, 1],
     [0, 1, 0]],

    [[0, 2, 2],
     [2, 2, 0]],

    [[3, 3, 0],
     [0, 3, 3]],

    [[4, 0, 0],
     [4, 4, 4]],

    [[0, 0, 5],
     [5, 5, 5]],

    [[6, 6, 6, 6]],

    [[7, 7],
     [7, 7]],
]


def nowaPlansza():
    plansza = [[0 for x in range(kolumny)]
             for y in range(wiersze)]
    plansza += [[1 for x in range(kolumny)]]
    return plansza


def usunWiersz(plansza, wiersz):
    del plansza[wiersz]
    return [[0 for i in range(kolumny)]] + plansza


def sprawdzKolizje(plansza, ksztalt, przesuniecie):
    przes_x, przes_y = przesuniecie
    for cy, wiersz in enumerate(ksztalt):
        for cx, komorka in enumerate(wiersz):
            if komorka and plansza[cy + przes_y][cx + przes_x]:
                return True
    return False


def obrocZgodnieZRuchemZegara(ksztalt): #obracanie ksztaltow
    return [[ksztalt[y][x] for y in range(len(ksztalt))]
                        for x in range(len(ksztalt[0]) - 1, -1, -1)]


def polaczMatryce(mat1, mat2, mat2_przes):
    przes_x, przes_y = mat2_przes
    for cy, wiersz in enumerate(mat2):
        for cx, wartosc in enumerate(wiersz):
            mat1[cy + przes_y - 1][cx + przes_x] += wartosc
    return mat1


class Tetris:
    def __init__(self):
        pygame.init()
        self.muzyka = True
        pygame.mixer.init()
        pygame.mixer.music.load('theme.ogg')
        pygame.mixer.music.play(-1, 0.0) #zapetlanie, odtwarzanie od poczatku
        pygame.key.set_repeat(210, 60) #powtarzalnosc wcisniec klawiszy

        self.szerokosc = rozmiarKomorek * (kolumny + 6)
        self.wysokosc = rozmiarKomorek * wiersze
        self.szerokoscBezMarginesu = rozmiarKomorek * kolumny
        self.kratyWTle = [[8 for x in range(kolumny)] for y in range(wiersze)]
        self.czcionka = pygame.font.Font(pygame.font.get_default_font(), 25)
        self.ekran = pygame.display.set_mode((self.szerokosc, self.wysokosc)) #okno
        self.nastepnyKlocek = ksztalty[rand(len(ksztalty))]
        self.init_game()

    def init_game(self):
        self.plansza = nowaPlansza()
        self.nowyKlocek()
        self.wynik = 0
        self.linie = 0
        self.poziom = 1
        pygame.time.set_timer(pygame.USEREVENT + 1, 1000)  # tworzy eventy w kolejce; set_timer(eventid,milisec)

    def nowyKlocek(self):
        self.klocek = self.nastepnyKlocek
        self.nastepnyKlocek = ksztalty[rand(len(ksztalty))]
        self.klocek_x = int(kolumny / 2 - len(self.klocek[0]) / 2) #klocek startuje od srodka z gory
        self.klocek_y = 0
        if sprawdzKolizje(self.plansza, self.klocek, (self.klocek_x, self.klocek_y)):
            self.gameover = True

    def rysujMatryce(self, matrix, przesuniecie):
        przes_x, przes_y = przesuniecie
        for y, wiersz in enumerate(matrix):
            for x, wartosc in enumerate(wiersz):
                if wartosc:
                    pygame.draw.rect(self.ekran, kolory[wartosc], pygame.Rect( #rysowanie klockow, draw.rect(surface,color,Rect,szerokosc)
                        (przes_x + x) * rozmiarKomorek,(przes_y + y) * rozmiarKomorek, rozmiarKomorek, rozmiarKomorek), 3)

    def ruch(self, delta):
        nowy_x = self.klocek_x + delta
        if nowy_x < 0:
            nowy_x = 0
        if nowy_x > kolumny - len(self.klocek[0]):
            nowy_x = kolumny - len(self.klocek[0])
        if not sprawdzKolizje(self.plansza, self.klocek, (nowy_x, self.klocek_y)):
            self.klocek_x = nowy_x

    def obrocKlocek(self):
        nowyKlocek = obrocZgodnieZRuchemZegara(self.klocek)
        if not sprawdzKolizje(self.plansza, nowyKlocek, (self.klocek_x, self.klocek_y)):
            self.klocek = nowyKlocek

    def upusc(self, manual):
        if not self.gameover and not self.paused:
            self.wynik += 1 * self.poziom
            self.klocek_y += 1
            if sprawdzKolizje(self.plansza, self.klocek, (self.klocek_x, self.klocek_y)):
                self.plansza = polaczMatryce(self.plansza, self.klocek, (self.klocek_x, self.klocek_y))
                self.nowyKlocek()
                wyczyszczoneWiersze = 0
                while True:
                    for i, wiersz in enumerate(self.plansza[:-1]):
                        if 0 not in wiersz:
                            self.plansza = usunWiersz(self.plansza, i)
                            wyczyszczoneWiersze += 1
                            break
                    else:
                        break
                self.punktacja(wyczyszczoneWiersze)
                return True
        return False

    def upuscNaSamDol(self):  # upuszczanie klocka na dol
        if not self.gameover and not self.paused:
            while not self.upusc(True):
                pass

    def wyswietlTekst(self, tekst, przesuniecie):
        x, y = przesuniecie
        for linia in tekst.splitlines():
            self.ekran.blit(self.czcionka.render(linia, False, (248, 248, 255), (0, 0, 0)), (x, y)) #wyswietlanie
            y += 32                                                             #blit(source,dest,area,special flags)

    def wysrodkujTekst(self, tekst):
        for i, linia in enumerate(tekst.splitlines()):
            wygladTekstu = self.czcionka.render(linia, False, (248, 248, 255), (0, 0, 0))
            wygladTekstu_x, wygladTekstu_y = wygladTekstu.get_size()
            wygladTekstu_x //= 2
            wygladTekstu_y //= 2
            self.ekran.blit(wygladTekstu, (self.szerokosc // 2 - wygladTekstu_x, self.wysokosc // 2 - wygladTekstu_y + i * 32))

    def punktacja(self, n):
        tabelaPunktacji = [0, 10, 20, 30, 40]
        self.linie += n
        self.wynik += tabelaPunktacji[n] * self.poziom
        if self.linie >= self.poziom * 10:
            self.poziom += 1
            nowaSzybkosc = 1000 - (self.poziom - 1)
            nowaSzybkosc = 100 if nowaSzybkosc < 100 else nowaSzybkosc
            pygame.time.set_timer(pygame.USEREVENT + 1, nowaSzybkosc)


    def start(self):
        if self.gameover:
            self.init_game()
            self.gameover = False

    def wlaczWylaczPauze(self):
        self.paused = not self.paused

    def wycisz(self):
        if self.muzyka:
            pygame.mixer.music.pause()
            self.muzyka = False
        else:
            pygame.mixer.music.unpause()
            self.muzyka = True

    def koniec(self):
        pygame.display.update()
        pygame.quit()


    def wlaczGre(self):
        self.gameover = False
        self.paused = False

        klawisze = {
            'ESCAPE': self.koniec,
            'LEFT': lambda: self.ruch(-1),
            'RIGHT': lambda: self.ruch(+1),
            'DOWN': lambda: self.upusc(True),
            'UP': self.obrocKlocek,
            'p': self.wlaczWylaczPauze,
            'm': self.wycisz,
            'SPACE ': self.upuscNaSamDol
        }

        while True: #glowna petla programu
            self.ekran.fill((0,0,0)) #czarny
            if self.gameover:
                self.wysrodkujTekst("Koniec gry!\nTwoj wynik: %d " % self.wynik)
            else:
                if self.paused:
                    self.wysrodkujTekst("Pauza\nNacisnij p, aby kontynuowac")
                else:
                    self.wyswietlTekst("Nastepny:", (self.szerokoscBezMarginesu + rozmiarKomorek, 1))
                    self.wyswietlTekst("wynik: %d\n\npoziom: %d \
                    \nlinie: %d" % (self.wynik, self.poziom, self.linie), (self.szerokoscBezMarginesu + rozmiarKomorek, rozmiarKomorek * 5))
                    self.rysujMatryce(self.kratyWTle, (0, 0)) #kratki w tle
                    self.rysujMatryce(self.plansza, (0, 0)) #klocki na planszy
                    self.rysujMatryce(self.klocek, (self.klocek_x, self.klocek_y)) #lecacy klocek
                    self.rysujMatryce(self.nastepnyKlocek, (kolumny + 1, 1)) #nastepny klocek
            pygame.display.update() #zaktualizowanie ekranu

            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 1:
                    self.upusc(True)
                elif event.type == pygame.QUIT:
                    self.koniec()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    for klawisz in klawisze:
                        if event.key == eval("pygame.K_" + klawisz):
                            klawisze[klawisz]()

app = Tetris()
app.wlaczGre()
