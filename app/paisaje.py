"""Diorama agrícola esquemático. La geometría es ilustrativa."""
import plotly.graph_objects as go


def paisaje(nombre, parada):
    fig = go.Figure()
    def bloque(x, y, z, largo, ancho, alto, color):
        fig.add_mesh3d(x=[x,x+largo,x+largo,x]*2, y=[y,y,y+ancho,y+ancho]*2,
                       z=[z]*4+[z+alto]*4, i=[0,0,4,4,0,0,1,1,2,2,3,3],
                       j=[1,2,5,6,1,5,2,6,3,7,0,4], k=[2,3,6,7,5,4,6,5,7,6,4,7],
                       color=color, flatshading=True, hoverinfo="skip")
    bloque(0,0,-1,12,9,1,"#ad7152")
    bloque(0,0,0,12,9,.16,"#dcba77")
    for x,y,h in [(1,7,3),(4,7.2,4),(7,7.4,2.6),(10,7,3.5)]:
        fig.add_mesh3d(x=[x-2,x+2,x+1.6,x-1.4,x],y=[y-1,y-1,y+1,y+1,y],
                       z=[.16]*4+[h],i=[0,1,2,3],j=[1,2,3,0],k=[4]*4,
                       color="#ab7e72",flatshading=True,hoverinfo="skip")
    for x,color in [(1,"#789351"),(5,"#ba8049"),(9,"#8e9952")]:
        for n in range(6):
            bloque(x+n*.42,1,.16,.27,4,.24,color)
    destinos = {"Rotaciones": (3.8, 2), "Estación climática": (8, 5), "Sensor de suelo": (1, 5.5)}
    # Antena de la estación y sonda, visibles desde cualquier orientación.
    bloque(8.8,5,.16,.18,.18,1.8,"#545c59")
    bloque(8.4,4.8,1.85,1.0,.65,.12,"#455d70")
    bloque(1,6,.16,.22,.22,.9,"#526355")
    bloque(.85,5.9,.95,.55,.4,.4,"#db933e")
    for etiqueta,(x,y) in destinos.items():
        fig.add_scatter3d(x=[x],y=[y],z=[2.3],mode="text",text=[etiqueta],
                          textfont=dict(size=12,color="#40372b"),hoverinfo="skip")
    # Camino de tierra, huellas paralelas y cercas bajas entre las parcelas.
    bloque(.2,5.05,.17,11.5,.72,.025,"#bd9868")
    for y in [5.18,5.52]:
        bloque(.3,y,.20,11.3,.065,.012,"#967951")
    for x in [0.8, 4.8, 8.8]:
        for y in [1,2.25,3.5,4.75]:
            bloque(x,y,.16,.12,.12,.52,"#79553e")
        for z in [.39,.58]:
            bloque(x,1,z,.09,3.85,.07,"#b8875a")
    # Adobe y cubierta a dos aguas en el refugio de la estación.
    bloque(9.6,5.85,.16,1.45,.96,.86,"#ce9868")
    fig.add_mesh3d(x=[9.45,11.2,9.45,11.2,9.45,11.2],
        y=[5.72,5.72,6.33,6.33,6.94,6.94],z=[1,1,1.52,1.52,1,1],
        i=[0,0,2,2,0,1],j=[1,3,3,5,2,3],k=[3,2,5,4,4,5],
        color="#944d3c",flatshading=True,hoverinfo="skip")
    bloque(10.02,5.81,.16,.34,.05,.62,"#654431")
    # Espigas agrupadas en una sola malla para las dos franjas sembradas.
    xs,ys,zs,ii,jj,kk=[],[],[],[],[],[]
    for campo in [1,9]:
        for fila in range(6):
            for planta in range(9):
                cx,cy=campo+fila*.42+.12,1.2+planta*.43
                n=len(xs)
                xs.extend([cx-.09,cx+.09,cx,cx+.045])
                ys.extend([cy,cy,cy+.12,cy+.06])
                zs.extend([.4,.4,.4,.68+.045*((planta+fila)%3)])
                for a,b,c in [(0,1,3),(1,2,3),(2,0,3)]:
                    ii.append(n+a)
                    jj.append(n+b)
                    kk.append(n+c)
    fig.add_mesh3d(x=xs,y=ys,z=zs,i=ii,j=jj,k=kk,color="#ceb65c",
                   flatshading=True,hoverinfo="skip")
    x,y=destinos[parada]
    bloque(x,y,.18,.9,1.5,.45,"#cb5636")
    bloque(x+.1,y+.6,.63,.7,.65,.52,"#f2ddaa")
    for lado in [-.14,.81]:
        for eje in [.12,1.05]:
            bloque(x+lado,y+eje,.16,.23,.43,.48,"#47463a")
    fig.update_traces(lighting=dict(ambient=.55,diffuse=.85,specular=.12,roughness=.94),lightposition=dict(x=-80,y=-120,z=170),selector=dict(type="mesh3d"))
    fig.update_layout(height=420,margin=dict(l=0,r=0,t=0,b=0),paper_bgcolor="#f5e9d6",
        scene=dict(bgcolor="#f5e9d6",aspectmode="data",dragmode="orbit",
                   camera=dict(eye=dict(x=1.25,y=-1.65,z=1.05)),
                   **{a:dict(visible=False) for a in ["xaxis","yaxis","zaxis"]}),
        uirevision=nombre,showlegend=False)
    return fig
