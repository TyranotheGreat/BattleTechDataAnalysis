with battles as
(
select attacking_mechdef_id, defending_mechdef_id , count(*) battles, sum(case when turn = 1 then 1 else 0 end) go_first_wins 
from 
(
select *, attacking_mechdef_id winner
from 
(
select 
	battle_id , 
	attacking_mechdef_id , 
	defending_mechdef_id, 
	round, 
	turn , 
	row_number() over (partition by battle_id order by round desc,turn desc) last_attack
from battlehistory
) a
where a.last_attack = 1
) b 
where attacking_mechdef_id = winner or defending_mechdef_id = winner 
group by attacking_mechdef_id, defending_mechdef_id
), final_data as
(
select 
	a.attacking_mechdef_id, 
	a.defending_mechdef_id, 
	sum(a.battles) total_wins, 
	sum(a.battles + coalesce(b.battles,0)) total_battles, 
	sum(a.go_first_wins + coalesce(b.go_first_wins,0)) total_first_player_wins	
from battles a
left join battles b on a.attacking_mechdef_id = b.defending_mechdef_id and a.defending_mechdef_id = b.attacking_mechdef_id
group by a.attacking_mechdef_id, a.defending_mechdef_id
)
select  
	attacking_mechdef_id, 
	defending_mechdef_id,
	case when attacking_mechdef_id = defending_mechdef_id then total_first_player_wins else total_wins end wins,
	total_battles
from final_data